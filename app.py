from fastapi import FastAPI, Depends, Request, HTTPException, Form
import uvicorn
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from db.db_connection import db_connect
from models.get_model import Items, Login
from models.schemas import ItemResponse
from models.bert_model import text_summarization


app = FastAPI()

# Enable session storage
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates("Templates")


# Root redirect
@app.get("/")
async def root():
    return RedirectResponse(url="/login", status_code=303)


# Exception handler
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return template.TemplateResponse("404.html", {"request": request}, status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


# Show all notes (only current user's notes)
@app.get("/all_notes", response_class=HTMLResponse)
async def get_all_notes(request: Request, db: Session = Depends(db_connect)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)

    items = db.query(Items).filter(Items.user_id == user_id).all()
    return template.TemplateResponse("get_note.html", {"request": request, "items": items})


# Add new note (linked to logged-in user)
@app.get("/notes", response_class=HTMLResponse)
async def notes_form(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)
    return template.TemplateResponse("post_note.html", {"request": request})


@app.post("/notes")
async def post_notes(
    request: Request,
    db: Session = Depends(db_connect),
    title: str = Form(...),
    description: str = Form(...),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)

    new_item = Items(title=title, description=description, user_id=user_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return RedirectResponse(url="/all_notes", status_code=303)


# Delete note
@app.post("/delete/{note_id}")
async def delete_notes(note_id: int, request: Request, db: Session = Depends(db_connect)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)

    note = db.query(Items).filter(Items.id == note_id, Items.user_id == user_id).first()
    if note:
        db.delete(note)
        db.commit()
    return RedirectResponse(url="/all_notes", status_code=303)


# Update note
@app.post("/update/{note_id}")
async def update_notes(note_id: int, item: ItemResponse, request: Request, db: Session = Depends(db_connect)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)

    note = db.query(Items).filter(Items.id == note_id, Items.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = item.title
    note.description = item.description
    db.commit()
    db.refresh(note)

    return {"id": note.id, "title": note.title, "description": note.description}


# Summarize note
@app.get("/summarize/{note_id}")
def summarize_note_get(request: Request, note_id: int, db: Session = Depends(db_connect)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login/", status_code=303)

    note = db.query(Items).filter(Items.id == note_id, Items.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    summary = text_summarization(note.description)
    return template.TemplateResponse("summarize_note.html", {"request": request, "note": note, "summary": summary})


# Signup
@app.get("/signup/", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("signup.html", {"request": request})


@app.post("/signup/")
def signup(
    request: Request,
    db: Session = Depends(db_connect),
    username: str = Form(...),
    password: str = Form(...),
):
    existing = db.query(Login).filter(Login.user_name == username).first()
    if existing:
        return template.TemplateResponse(
            "signup.html",
            {"request": request, "error": "User already exists"},
            status_code=400,
        )

    new_user = Login(user_name=username, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session["user_id"] = new_user.user_id
    return RedirectResponse(url="/all_notes", status_code=303)


# Login
@app.get("/login/", response_class=HTMLResponse)
def get_login_page(request: Request):
    return template.TemplateResponse("login.html", {"request": request})


@app.post("/login/")
def post_login_page(request: Request, db: Session = Depends(db_connect), username: str = Form(...), password: str = Form(...)):
    user = db.query(Login).filter(Login.user_name == username, Login.password == password).first()
    if not user:
        return template.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )

    request.session["user_id"] = user.user_id
    return RedirectResponse(url="/all_notes", status_code=303)


# Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login/", status_code=303)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

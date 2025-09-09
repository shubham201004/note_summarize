from fastapi import FastAPI,Depends,Request,HTTPException
import uvicorn
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from db.db_connection import db_connect
from models.get_model import Items
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from models.get_model import Items
from models.schemas import ItemResponse
from models.bert_model import text_summarization
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.templating import Jinja2Templates

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates('Templates')
@app.get("/")
async def root():
    return RedirectResponse(url="/notes", status_code=303)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return template.TemplateResponse("404.html", {"request": request}, status_code=404)
    return await app.default_exception_handler(request, exc) # type: ignore
@app.get('/all_notes',response_class=HTMLResponse)
async def get_all_notes(request:Request,db:Session=Depends(db_connect)):
    items = db.query(Items).all()
    return template.TemplateResponse('get_note.html',{"request":request,"items":items})

@app.get("/notes", response_class=HTMLResponse)
async def notes_form(request: Request):
    return template.TemplateResponse("post_note.html", {"request": request})


@app.post('/notes')
async def post_notes(request:Request,db:Session=Depends(db_connect),title:str = Form(...),description:str=Form(...)):
    new_item = Items(title=title,description=description)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    # return template.TemplateResponse('get_note.html',{"request":request,"item":new_item})
    return RedirectResponse(url="/all_notes", status_code=303)


@app.post('/delete/{note_id}')
async def delete_notes(note_id,db:Session=Depends(db_connect)):
    note = db.query(Items).filter(Items.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
    return RedirectResponse(url="/all_notes", status_code=303)


@app.post("/update/{note_id}")
async def update_notes(
    note_id: int,
    item: ItemResponse,   # request body
    db: Session = Depends(db_connect)
):
    note = db.query(Items).filter(Items.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = item.title
    note.description = item.description
    db.commit()
    db.refresh(note)

    return {"id": note.id, "title": note.title, "description": note.description}

@app.get('/summarize/{note_id}')
def summarize_note_get(request:Request,note_id: int, db: Session = Depends(db_connect)):
    note = db.query(Items).filter(Items.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    summary = text_summarization(note.description)
    return template.TemplateResponse('summarize_note.html',{"request":request,"note":note,"summary":summary})

@app.post('/summarize/')
def summarize_note_post():
    return 'Hello WOrld'


if __name__ =="__main__":
    uvicorn.run("app:app",host="127.0.0.1",port=8000,reload=True)
$(document).ready(function () {
    console.log("JS loaded");

    // Show update form on click
    $(".update-btn").click(function (e) {
        e.preventDefault();
        console.log("Clikecck")
        let noteItem = $(this).closest(".note-item");

        // get current values
        let currentTitle = noteItem.find(".note-title").text();
        let currentDesc = noteItem.find(".note-desc").text();

        // fill into form inputs
        noteItem.find("input[name='title']").val(currentTitle);
        noteItem.find("input[name='description']").val(currentDesc);
        console.log(currentDesc)
        console.log(currentTitle)

        // toggle visibility
        noteItem.find(".note-display").hide();
        noteItem.find(".update-form").show();
    });

    // Delete confirmation
    $(".delete-btn").click(function () {
        return confirm("Are you sure to delete this note?");
    });
    $(".cancel-btn").click(function () {
        let noteItem = $(this).closest(".note-item");
        noteItem.find(".update-form").hide();     // hide the edit form
        noteItem.find(".note-display").show();    // show title+desc again
    });
    // Handle update form submission (AJAX)
    $(".update-form").on("submit", function (e) {
        e.preventDefault();

        let form = $(this);
        let noteItem = form.closest(".note-item");
        let id = form.data("id");

        let title = form.find("input[name='title']").val().trim();
        let description = form.find("input[name='description']").val().trim();

        if (!title || !description) {
            alert("Both fields are required!");
            return;
        }

        $.ajax({
            url: "/update/" + id,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ title: title, description: description }),
            success: function (response) {
                // update display instantly
                noteItem.find(".note-title").text(title);
                noteItem.find(".note-desc").text(description);

                // hide form, show display
                form.hide();
                noteItem.find(".note-display").show();

                alert("Note updated successfully!");
            },
            error: function () {
                alert("Failed to update note.");
            }
        });
    });
    function initReadMore() {
  $(".add-read-more").each(function () {
    let $this = $(this);
    let limit = parseInt($this.data("limit")) || 300;
    let text = $this.text().trim();

    if (text.length > limit) {
      let visibleText = text.substring(0, limit);
      let hiddenText = text.substring(limit);

      $this.html(
        visibleText +
        "<span class='hidden-text'>" + hiddenText + "</span>" +
        "<span class='read-toggle'>...read more</span>"
      );

      $this.on("click", ".read-toggle", function () {
        $this.toggleClass("expanded");
        $(this).text($this.hasClass("expanded") ? " read less" : "...read more");
      });
    }
  });
}

$(document).ready(initReadMore);

});

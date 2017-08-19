// Enables the hiding/showing of a comment or the
// form to edit that comment
function toggleVisibility(commentKey) {

    // get needed IDs
    commentId = "comment|".concat(commentKey)
    editId = "edit|".concat(commentKey)
    console.log(editId)

    // get elements
    comment = document.getElementById(commentId)
    edit = document.getElementById(editId)

    // toggle visibility
    if (edit.style.display === 'none') {
        edit.style.display = null;
        comment.style.display = 'none';
    } else {
        edit.style.display = 'none';
        comment.style.display = null;
    }
}

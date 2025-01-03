function openCreatePostModal() {
    document.getElementById('createPostModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  }
  
  function closeCreatePostModal() {
    document.getElementById('createPostModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('post-content');
    const postButton = document.getElementById('post-button');
  
    textarea.addEventListener('input', function() {
      postButton.disabled = textarea.value.trim() === '';
    });
  });
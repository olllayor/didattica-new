const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "{{ csrf_token }}";

document.addEventListener("DOMContentLoaded", () => {
    // Element selectors
    const chatMessagesContainer = document
        .getElementById("chat-messages")
        .querySelector("div");
    const chatInput = document.getElementById("chat-input");
    const submitButton = document.getElementById("submit-button");
    const stopButton = document.getElementById("stop-button");
    const loadingState = document.getElementById("loading-state");
    const imagePreview = document.getElementById("image-preview");
    const attachInput = document.getElementById("attach-input");
    const attachButton = document.getElementById("attach-button");
    const searchButton = document.getElementById("search-button");

    // Variables
    let isLoading = false;
    let abortController = null;
    let hasSentMessage = false;
    let isAuthenticated = false;
    let userHasScrolled = false;
    
    // File handling functions
    function handleFilePreview(files) {
        imagePreview.innerHTML = ""; // Clear existing previews

        if (files.length > 0) {
            imagePreview.classList.remove("hidden");

            Array.from(files).forEach((file, index) => {
                if (file.type.startsWith("image/")) {
                    const reader = new FileReader();
                    const previewContainer = document.createElement("div");
                    previewContainer.className = "relative group";

                    reader.onload = (e) => {
                        previewContainer.innerHTML = `
                        <div class="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200 group">
                          <img src="${e.target.result}" class="w-full h-full object-cover" alt="Preview"/>
                          <div class="absolute inset-0 bg-black opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
                          <button
                            class="absolute top-1 right-1 p-1 rounded-full bg-white/80 opacity-0 group-hover:opacity-100 hover:bg-white transition-all duration-200 shadow-sm"
                            onclick="removePreviewImage(${index})"
                            aria-label="Remove image"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            >
                              <line x1="18" y1="6" x2="6" y2="18"></line>
                              <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                          </button>
                        </div>
                      `;
                    };

                    reader.readAsDataURL(file);
                    imagePreview.appendChild(previewContainer);
                }
            });
        } else {
            imagePreview.classList.add("hidden");
        }
    }

    function removePreviewImage(index) {
        const fileList = Array.from(attachInput.files);
        const dt = new DataTransfer();

        fileList.forEach((file, i) => {
            if (i !== index) dt.items.add(file);
        });

        attachInput.files = dt.files;
        handleFilePreview(attachInput.files);

        if (attachInput.files.length === 0) {
            imagePreview.classList.add("hidden");
        }
    }

    // Make function available globally
    window.removePreviewImage = removePreviewImage;

    // Authentication functions
    async function checkAuth() {
        try {
            const response = await fetch("/ai/auth/check/", {
                credentials: "include",
            });
            const data = await response.json();
            isAuthenticated = response.ok;
            if (!isAuthenticated) {
                window.location.href = data.login_url || "/accounts/login/?next=/ai/";
            }
        } catch (error) {
            console.error("Auth check failed:", error);
            window.location.href = "/accounts/login/?next=/ai/";
        }
    }

    // UI helper functions
    function resizeTextarea() {
        chatInput.style.height = "auto";
        const maxHeight = Math.min(200, window.innerHeight * 0.4);
        chatInput.style.height = Math.min(chatInput.scrollHeight, maxHeight) + "px";
    }

    function scrollToLatestMessage(force = false) {
        const chatContainer = chatMessagesContainer.parentElement;
        const threshold = 100; // pixels from bottom to trigger auto-scroll
        const isNearBottom =
            chatContainer.scrollHeight -
            chatContainer.scrollTop -
            chatContainer.clientHeight <
            threshold;

        if (force || isNearBottom) {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: "smooth",
            });
        }
    }

    function setupScrollObserver() {
        const chatContainer = chatMessagesContainer.parentElement;
        let lastScrollTop = chatContainer.scrollTop;

        chatContainer.addEventListener("scroll", () => {
            const isScrollingUp = chatContainer.scrollTop < lastScrollTop;
            if (isScrollingUp) {
                userHasScrolled = true;
            }

            // Reset userHasScrolled when user scrolls to bottom
            const isAtBottom =
                chatContainer.scrollHeight -
                chatContainer.scrollTop -
                chatContainer.clientHeight <
                10;
            if (isAtBottom) {
                userHasScrolled = false;
            }

            lastScrollTop = chatContainer.scrollTop;
        });
    }

    // Chat message functions
    function addChatMessage(message, isUser = false, isStreaming = false, images = []) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `flex ${
            isUser ? "justify-end" : "justify-start"
        } mb-4`;

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = `max-w-full rounded-2xl p-3 ${
            isUser ? "bg-[#E8E8E880] text-black" : "bg-white"
        }`;

        // Add images if present
        if (images && images.length > 0) {
            const imagesContainer = document.createElement("div");
            imagesContainer.className = "message-images";

            images.forEach(imageUrl => {
                const img = document.createElement("img");
                img.src = imageUrl;
                img.className = "chat-image";
                img.alt = "Uploaded image";
                imagesContainer.appendChild(img);
            });

            bubbleDiv.appendChild(imagesContainer);
        }

        if (!isUser && message.startsWith("Error:")) {
            bubbleDiv.textContent = message;
            bubbleDiv.style.backgroundColor = "#fdecea";
            bubbleDiv.style.color = "#b71c1c";
        } else if (!isUser && isStreaming) {
            const textSpan = document.createElement("span");
            bubbleDiv.appendChild(textSpan);
            const cursor = document.createElement("span");
            cursor.className = "cursor";
            cursor.textContent = "...";
            bubbleDiv.appendChild(cursor);
            messageDiv.appendChild(bubbleDiv);
            chatMessagesContainer.appendChild(messageDiv);
            scrollToLatestMessage();
            return {textSpan, cursor};
        } else {
            if (isUser) {
                const messageContent = document.createElement("div");
                messageContent.textContent = message;
                bubbleDiv.appendChild(messageContent);
            } else {
                const parsed = marked.parse(message);
                const messageContent = document.createElement("div");
                messageContent.innerHTML = parsed;
                bubbleDiv.appendChild(messageContent);

                // Code block styling
                bubbleDiv.querySelectorAll("pre code").forEach((block) => {
                    // Get language class if specified
                    const langClass = block.className.match(/language-([^\s]+)/);
                    const language = langClass ? langClass[1] : "plaintext";

                    block.className = `language-${language} font-mono text-sm`;
                    const pre = block.parentElement;
                    pre.className =
                        "group relative bg-gray-50 rounded-md p-4 my-3 overflow-x-auto";

                    // Add copy button
                    const copyButton = document.createElement("button");
                    copyButton.className =
                        "absolute top-2 right-2 p-1 rounded text-gray-500 hover:bg-gray-200 opacity-0 group-hover:opacity-100";
                    copyButton.innerHTML = `
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                        <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                      </svg>
                    `;
                    copyButton.addEventListener("click", () => {
                        navigator.clipboard.writeText(block.textContent);
                    });
                    pre.appendChild(copyButton);
                });

                // Style inline code
                bubbleDiv
                    .querySelectorAll("code:not(pre code)")
                    .forEach((block) => {
                        block.className =
                            "bg-gray-100 rounded px-1.5 py-0.5 font-mono text-sm text-gray-800";
                    });

                // Style blockquotes
                bubbleDiv.querySelectorAll("blockquote").forEach((block) => {
                    block.className =
                        "border-l-4 border-gray-200 pl-4 my-4 italic text-gray-600";
                });

                // Style lists
                bubbleDiv.querySelectorAll("ul, ol").forEach((list) => {
                    list.className = "my-3 pl-5";
                });

                // Style headings
                ["h1", "h2", "h3", "h4", "h5", "h6"].forEach((tag) => {
                    bubbleDiv.querySelectorAll(tag).forEach((heading) => {
                        heading.className = "font-bold my-3";
                    });
                });
            }
        }
        messageDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(messageDiv);
        scrollToLatestMessage();
        return null;
    }

    // Update UI state based on streaming status
    function updateLoadingState() {
        if (isLoading) {
            submitButton.classList.add("hidden");
            stopButton.classList.remove("hidden");
            loadingState.classList.remove("hidden");
        } else {
            submitButton.classList.remove("hidden");
            stopButton.classList.add("hidden");
            loadingState.classList.add("hidden");
        }
    }

    // Send a chat message and stream the AI response
    async function sendChatMessage(body, headers, useFormData) {
        if (!isAuthenticated) {
            window.location.href = "/accounts/login/?next=" + encodeURIComponent(window.location.pathname);
            return;
        }

        abortController = new AbortController();
        const signal = abortController.signal;

        try {
            const response = await fetch("/ai/chat/", {
                method: "POST",
                headers: headers,
                credentials: "include",
                body: body,
                signal: signal,
            });
            
            if (response.status === 401 || response.status === 403) {
                const data = await response.json();
                window.location.href = data.login_url || "/accounts/login/";
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const streamingMessage = addChatMessage("", false, true);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;
            let accumulatedText = "";
            
            while (!done) {
                const {value, done: doneReading} = await reader.read();
                done = doneReading;
                const chunk = decoder.decode(value, {stream: true});
                accumulatedText += chunk;
                streamingMessage.textSpan.innerHTML = marked.parse(accumulatedText);
                
                if (!userHasScrolled) {
                    scrollToLatestMessage(true);
                }
            }
            
            streamingMessage.cursor.remove();
        } catch (error) {
            if (error.name === "AbortError") {
                console.log("Streaming aborted by the user.");
            } else {
                console.error("Error during fetch:", error);
                addChatMessage(
                    "Error: Failed to send message. Please try again.",
                    false
                );
            }
        } finally {
            isLoading = false;
            updateLoadingState();
            abortController = null;
        }
    }

    // Handle message submission
    function handleSubmit(event) {
        if (event) event.preventDefault();
        
        const prompt = chatInput.value.trim();
        const files = attachInput.files;

        // Only proceed if there is a prompt or attached files
        if (!prompt && files.length === 0) return;
        
        // Create array of image URLs for display
        const imageUrls = [];
        if (files.length > 0) {
            for (let i = 0; i < files.length; i++) {
                const url = URL.createObjectURL(files[i]);
                imageUrls.push(url);
            }
        }

        addChatMessage(prompt, true, false, imageUrls);

        chatInput.value = "";
        resizeTextarea();
        
        if (!hasSentMessage) {
            hasSentMessage = true;
            const modelSelectWrapper = document.getElementById("model-select-wrapper");
            if (modelSelectWrapper) {
                modelSelectWrapper.style.display = "none";
            }
            const modelSelectorContent = document.getElementById("model-selector-content");
            if (modelSelectorContent) {
                modelSelectorContent.classList.remove("justify-between");
                modelSelectorContent.classList.add("justify-center");
            }
        }
        
        isLoading = true;
        updateLoadingState();
        
        // Determine if there are attached files
        let useFormData = attachInput.files.length > 0;
        let body, headers = {"X-CSRFToken": csrftoken};
        
        if (useFormData) {
            // Create a FormData object and append prompt, model, and files
            body = new FormData();
            body.append("prompt", prompt);
            const modelSelector = document.querySelector("select");
            body.append("model", modelSelector.value);
            for (let i = 0; i < attachInput.files.length; i++) {
                body.append("images", attachInput.files[i]);
            }
        } else {
            headers["Content-Type"] = "application/json";
            body = JSON.stringify({
                prompt: prompt,
                model: document.querySelector("select").value,
            });
        }
        
        // Send the message (and attachments, if any)
        sendChatMessage(body, headers, useFormData);
        attachInput.value = "";
        imagePreview.innerHTML = ""; // Clear previews after submission
        imagePreview.classList.add("hidden");
    }

    // Stop the ongoing streaming response
    function handleStop() {
        if (abortController) {
            abortController.abort();
            abortController = null;
        }
        isLoading = false;
        updateLoadingState();
    }
    
    // Improved mobile viewport handling
    window.visualViewport.addEventListener("resize", () => {
        document.documentElement.style.height = `${window.visualViewport.height}px`;
        resizeTextarea();

        const isMobile = window.innerWidth <= 768;
        if (isMobile && document.activeElement === chatInput) {
            chatMessagesContainer.parentElement.scrollTo({
                top: chatMessagesContainer.parentElement.scrollHeight,
                behavior: "smooth",
            });
            requestAnimationFrame(() => {
                chatInput.scrollIntoView({
                    block: "nearest",
                    behavior: "smooth",
                });
            });
        }
    });

    // Event listeners
    chatInput.addEventListener("input", resizeTextarea);
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit(event);
        }
    });
    
    submitButton.addEventListener("click", handleSubmit);
    stopButton.addEventListener("click", handleStop);
    
    // When attach button is clicked, trigger the hidden file input
    attachButton.addEventListener("click", () => {
        attachInput.click();
    });
    
    // Update the attachInput event listener
    attachInput.addEventListener("change", () => {
        if (attachInput.files.length > 0) {
            handleFilePreview(attachInput.files);
        } else {
            imagePreview.classList.add("hidden");
        }
    });
    
    // Scroll chat input into view when focused (mobile)
    chatInput.addEventListener("focus", () => {
        if (window.innerWidth <= 768) {
            requestAnimationFrame(() => {
                chatInput.scrollIntoView({block: "end", behavior: "smooth"});
            });
        }
    });
    
    // Set initial model name and update on change
    const select = document.querySelector("select");
    const selectedModelName = select.selectedOptions[0].textContent;
    document.getElementById("selected-model-name").textContent = selectedModelName;
    
    select.addEventListener("change", (event) => {
        const newModelName = event.target.selectedOptions[0].textContent;
        document.getElementById("selected-model-name").textContent = newModelName;
    });
    
    // Handle post loading from community integration
    document.addEventListener('loadPostInChat', (event) => {
        const { postId, content, image } = event.detail;
        
        // Prepare the chat input
        chatInput.value = content;
        
        // Handle image if present
        if (image) {
            const imagePreview = document.getElementById('image-preview');
            imagePreview.classList.remove('hidden');
            
            const previewContainer = document.createElement('div');
            previewContainer.className = 'relative inline-block';
            previewContainer.innerHTML = `
                <img src="${image}" alt="Post image" class="h-20 w-20 object-cover rounded-lg">
                <button onclick="removePreviewImage(0)" class="absolute -top-2 -right-2 bg-white rounded-full p-1 shadow-md">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;
            imagePreview.appendChild(previewContainer);
    
            // Create a file from the image URL and add it to the file input
            fetch(image)
                .then(res => res.blob())
                .then(blob => {
                    const file = new File([blob], "post_image.jpg", { type: "image/jpeg" });
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    document.getElementById('attach-input').files = dt.files;
                });
        }
    
        // Auto-resize the textarea
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
    });
    
    // Initialize
    checkAuth();
    setupScrollObserver();
});
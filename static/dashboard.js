
     console.log("JS LOADED");

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookies[i].substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        const csrftoken = getCookie('csrftoken');


        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const leftSidebar = document.getElementById('leftSidebar');
        const topNavbar = document.getElementById('topNavbar');

        mobileMenuToggle.addEventListener('click', () => {
            leftSidebar.classList.toggle('mobile-open');
            mobileMenuToggle.classList.toggle('active');
            document.body.classList.toggle('sidebar-open');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (leftSidebar.classList.contains('mobile-open') && 
                !leftSidebar.contains(e.target) && 
                !mobileMenuToggle.contains(e.target)) {
                leftSidebar.classList.remove('mobile-open');
                mobileMenuToggle.classList.remove('active');
                document.body.classList.remove('sidebar-open');
            }
        });


        // Media overlay actions
        document.querySelectorAll('.media-action').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const icon = this.querySelector('i');
                if (icon.classList.contains('fa-heart')) {
                    icon.classList.toggle('fa-regular');
                    icon.classList.toggle('fa-solid');
                    this.style.background = icon.classList.contains('fa-solid') ? 'var(--electric-pink)' : 'rgba(255,255,255,0.2)';
                }
                if (icon.classList.contains('fa-bookmark')) {
                    icon.classList.toggle('fa-regular');
                    icon.classList.toggle('fa-solid');
                    this.style.background = icon.classList.contains('fa-solid') ? 'var(--royal-purple)' : 'rgba(255,255,255,0.2)';
                }
            });
        });

        // Filter tabs
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Mood tracker
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Affirmation save
        const affirmationSave = document.getElementById('affirmationSave');
        affirmationSave.addEventListener('click', function() {
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-regular');
            icon.classList.toggle('fa-solid');
            this.style.color = icon.classList.contains('fa-solid') ? 'var(--electric-pink)' : '';
        });

        // Load more
        const loadMoreBtn = document.getElementById('loadMoreBtn');

        if (loadMoreBtn) {

            loadMoreBtn.addEventListener('click', function() {

                this.classList.add('loading');

                setTimeout(() => {
                    this.classList.remove('loading');
                }, 1500);

            });

        }

        // Follow buttons
        document.querySelectorAll('.creator-follow').forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.textContent === 'Follow') {
                    this.textContent = 'Following';
                    this.classList.add('following');
                } else {
                    this.textContent = 'Follow';
                    this.classList.remove('following');
                }
            });
        });

        // Profile dropdown
        const navProfile = document.querySelector('.nav-profile');
        navProfile.addEventListener('click', () => {
            navProfile.classList.toggle('dropdown-open');
        });

        const notifBtn = document.getElementById('notifBtn');
        const notifDropdown = document.getElementById('notifDropdown');

        const notifClearBtn = document.querySelector('.notif-clear-btn');

        if (notifBtn && notifDropdown) {
            notifBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                notifDropdown.classList.toggle('open');
                notifBtn.classList.toggle('active');
            });

            notifDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });

            document.addEventListener('click', (e) => {
                if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
                    notifDropdown.classList.remove('open');
                    notifBtn.classList.remove('active');
                }
            });
        }

        if (notifClearBtn) {
            notifClearBtn.addEventListener('click', () => {
                const unreadCards = notifDropdown.querySelectorAll('.notif-card.unread');
                unreadCards.forEach(card => {
                    card.classList.remove('unread');
                    card.classList.add('read');
                });

                const badge = notifBtn.querySelector('.notif-badge');
                const notifCount = document.querySelector('.notif-count');
                if (badge) {
                    badge.textContent = '0';
                }
                if (notifCount) {
                    notifCount.textContent = '0 New';
                }

                notifClearBtn.textContent = 'All read';
                notifClearBtn.disabled = true;
                notifClearBtn.style.opacity = '0.65';
            });
        }

        document.addEventListener('click', (e) => {
            if (!navProfile.contains(e.target)) {
                navProfile.classList.remove('dropdown-open');
            }
        });

        // Navbar scroll behavior
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            if (currentScroll > 100) {
                topNavbar.classList.add('scrolled');
            } else {
                topNavbar.classList.remove('scrolled');
            }
            lastScroll = currentScroll;
        });


        // OPEN COMMENT
            function openComments(id){
                const el = document.getElementById("comments-" + id);
                if (!el) return;

                el.classList.toggle("open");
            }

        // CLOSE COMMENT
        function closeComment(id) {
            document.getElementById("comment-" + id).style.display = "none";
        }


        // LIKE (AJAX, NO REFRESH)
           document.querySelectorAll(".like-btn").forEach(btn => {

                btn.addEventListener("click", async function(e) {

                    e.preventDefault();

                    const postId = this.dataset.id;
                    const icon = this.querySelector("i");
                    const count = this.querySelector(".like-count");

                    const response = await fetch(`/like/${postId}/`, {
                        method: "POST",

                        headers: {
                            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });

                    const data = await response.json();

                    count.textContent = data.likes;

                    if (data.liked) {
                        icon.classList.remove("fa-regular");
                        icon.classList.add("fa-solid");

                        this.style.color = "var(--electric-pink)";
                        this.style.background = "rgba(147, 51, 234, 0.08)";
                    } else {
                        icon.classList.remove("fa-solid");
                        icon.classList.add("fa-regular");

                        this.style.color = "";
                        this.style.background = "";
                    }

                });

            });



        // BOOKMARK (placeholder)

            document.querySelectorAll(".bookmark-btn").forEach(btn => {

                btn.addEventListener("click", async function () {

                    const postId = this.dataset.id;

                    const icon = this.querySelector("i");

                    const count = this.querySelector(".bookmark-count");

                    try {

                        const res = await fetch(`/bookmark/${postId}/`, {

                            method: "POST",

                            headers: {
                                "X-CSRFToken": csrftoken,
                                "X-Requested-With": "XMLHttpRequest"
                            }

                        });

                        const data = await res.json();

                        if (data.bookmarked) {

                            icon.classList.remove("fa-regular");
                            icon.classList.add("fa-solid");

                            this.classList.add("active");

                        } else {

                            icon.classList.remove("fa-solid");
                            icon.classList.add("fa-regular");

                            this.classList.remove("active");

                        }

                        count.textContent = data.count;

                    } catch(err) {

                        console.error("Bookmark error:", err);

                    }

                });

            });

        //AJAX COMMENTS

            document.querySelectorAll(".comment-form").forEach(form => {

                form.addEventListener("submit", async function(e) {

                    e.preventDefault();

                    const postId = this.dataset.id;
                    const input = this.querySelector("input[name='text']");
                    const text = input.value.trim();

                    if (!text) return;

                    const formData = new FormData();
                    formData.append("text", text);
                    formData.append("csrfmiddlewaretoken", this.querySelector("[name=csrfmiddlewaretoken]").value);

                    try {

                        const res = await fetch(`/comment/${postId}/`, {
                            method: "POST",
                            body: formData
                        });

                        const data = await res.json();

                        if (!data.success) return;

                        const commentBox1 = document.getElementById("comments-" + postId);

                        if (!commentBox1) return;

                        // CREATE COMMENT

                        const commentBox = document.getElementById("comments-" + postId);

                        const wrapper = document.createElement("div");
                        wrapper.className = "comment";
                        wrapper.id = `comment-${data.comment_id}`;

                        wrapper.innerHTML = `
                            <div class="comment-left">
                                <strong>${ data.username }: </strong>
                                <span>${ data.text }</span>
                            </div>

                            <button class="delete-comment-btn" data-id="${data.comment_id}" type="button">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        `;

                        /* animation start state */
                        wrapper.style.opacity = "0";
                        wrapper.style.transform = "translateY(10px)";

                        commentBox.prepend(wrapper);

                        /* animation */
                        requestAnimationFrame(() => {
                            wrapper.style.transition = "0.25s ease";
                            wrapper.style.opacity = "1";
                            wrapper.style.transform = "translateY(0)";
                        });

                        // 👉 IMPORTANT: NEW COMMENT GOES TOP
                        commentBox.prepend(wrapper);

                        // CLEAR INPUT
                        input.value = "";

                        // UPDATE COUNT
                        const card = commentBox.closest(".feed-card");
                        const countEl = card.querySelector(".comment-count");

                        if (countEl) {
                            countEl.textContent = data.comment_count;
                        }

                    } catch (err) {
                        console.error("Comment error:", err);
                    }

                });

            });



         //delete comments

           document.addEventListener("click", async (e) => {
                const btn = e.target.closest(".delete-comment-btn");
                if (!btn) return;

                const commentId = btn.dataset.id;
                const commentEl = document.getElementById("comment-" + commentId);

                const res = await fetch(`/comment/delete/${commentId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken
                    }
                });

                const data = await res.json();

                if (data.success) {

                    // GET FEED CARD FIRST
                    const feedCard = commentEl.closest(".feed-card");

                    // GET COUNTER
                    const countEl = feedCard.querySelector(".comment-count");

                    // UPDATE COUNTER
                    if (countEl) {
                        countEl.textContent = data.comment_count;
                    }

                    // ANIMATE DELETE
                    commentEl.style.transition = "0.2s ease";
                    commentEl.style.opacity = "0";
                    commentEl.style.transform = "translateX(20px)";

                    // REMOVE AFTER ANIMATION
                    setTimeout(() => {
                        commentEl.remove();
                    }, 200);
                


                }
            });
      
            console.log("delete JS loaded");



            //CONFIRMATION MODAL

            let postToDelete = null;

            const modal = document.getElementById("deleteModal");
            const cancelBtn = document.getElementById("cancelDelete");
            const confirmBtn = document.getElementById("confirmDelete");

            // OPEN MODAL
            document.addEventListener("click", function(e){

                const btn = e.target.closest(".delete-post-btn");
                if (!btn) return;

                postToDelete = btn.closest(".feed-card");
                postToDelete.dataset.id = btn.dataset.id;

                modal.style.display = "flex";
            });

            // CANCEL
            cancelBtn.addEventListener("click", () => {
                modal.style.display = "none";
                postToDelete = null;
            });

            // CONFIRM DELETE
            confirmBtn.addEventListener("click", async () => {

                if (!postToDelete) return;

                const postId = postToDelete.dataset.id;

                const res = await fetch(`/post/delete/${postId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await res.json();

                if (data.success) {

                    postToDelete.style.transition = "0.3s";
                    postToDelete.style.opacity = "0";
                    postToDelete.style.transform = "scale(0.9)";

                    setTimeout(() => {
                        postToDelete.remove();
                    }, 300);
                }

                modal.style.display = "none";
                postToDelete = null;
            });

            // CLOSE ON BACKDROP CLICK
            modal.addEventListener("click", (e) => {
                if (e.target === modal) {
                    modal.style.display = "none";
                    postToDelete = null;
                }
            });
            

            function loadFeed(feedType){

                fetch(`/load-feed/?feed=${feedType}`)
                .then(response => response.json())
                .then(data => {

                    document.getElementById("masonryFeed").innerHTML =
                        data.html;

                });

            }

            document
            .getElementById("for-you-btn")
            .addEventListener("click", function(){

                loadFeed("for_you");

            });

            document
            .getElementById("following-btn")
            .addEventListener("click", function(){

                loadFeed("following");

            });

            const forYouBtn = document.getElementById("for-you-btn");
            const followingBtn = document.getElementById("following-btn");

            forYouBtn.addEventListener("click", () => {

                forYouBtn.classList.add("active");
                followingBtn.classList.remove("active");

            });

            followingBtn.addEventListener("click", () => {

                followingBtn.classList.add("active");
                forYouBtn.classList.remove("active");

            });
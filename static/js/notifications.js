document.addEventListener("DOMContentLoaded", function () {
    const rowsPerPage = 8;
    let currentPage = 1;

    const notificationCards = document.querySelectorAll(".card-body"); 
    const paginationContainer = document.querySelector(".pagination-numbers-container");
    const prevPage = document.getElementById("prevPage");
    const nextPage = document.getElementById("nextPage");

    function displayRows() {
        // Hide all notification cards first
        notificationCards.forEach(card => card.style.display = "none");

        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        
        notificationCards.forEach((card, index) => {
            if (index >= startIndex && index < endIndex) {
                card.style.display = "block"; 
            }
        });

        updatePagination();
    }

    function updatePagination() {
        paginationContainer.innerHTML = ""; 

        const totalPages = Math.ceil(notificationCards.length / rowsPerPage);

        for (let i = 1; i <= totalPages; i++) {
            let li = document.createElement("li");
            li.classList.add("page-item");
            if (i === currentPage) li.classList.add("active");

            let a = document.createElement("a");
            a.classList.add("page-link");
            a.href = "#";
            a.innerText = i;
            a.addEventListener("click", function (e) {
                e.preventDefault();
                currentPage = i;
                displayRows();
            });

            li.appendChild(a);
            paginationContainer.appendChild(li);
        }

        prevPage.parentElement.classList.toggle("disabled", currentPage === 1);
        nextPage.parentElement.classList.toggle("disabled", currentPage === totalPages);
    }

    prevPage.addEventListener("click", function (e) {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            displayRows();
        }
    });

    nextPage.addEventListener("click", function (e) {
        e.preventDefault();
        const totalPages = Math.ceil(notificationCards.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            displayRows();
        }
    });

    displayRows(); 
});
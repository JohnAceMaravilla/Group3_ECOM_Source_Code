// Select All Checkboxes and Cell Click
document.addEventListener("DOMContentLoaded", function () {
   const selectAllCheckbox = document.getElementById("selectAll");
   const checkboxes = document.querySelectorAll(".form-check-input[name='user_ids']");
   const rows = document.querySelectorAll("tbody tr");

   selectAllCheckbox.addEventListener("change", function () {
      checkboxes.forEach(checkbox => {
         checkbox.checked = selectAllCheckbox.checked;
         checkbox.closest("tr").classList.toggle("selected-row", selectAllCheckbox.checked);
      });
   });

   rows.forEach(row => {
       row.addEventListener("click", function (event) {
           if (event.target.type === "checkbox") return;

           const checkbox = this.querySelector(".form-check-input[name='user_ids']");
           if (checkbox) {
               checkbox.checked = !checkbox.checked;
               this.classList.toggle("selected-row", checkbox.checked);
           }
       });
   });

   // 
   checkboxes.forEach(checkbox => {
      checkbox.addEventListener("change", function () {
         this.closest("tr").classList.toggle("selected-row", this.checked);
         selectAllCheckbox.checked = [...checkboxes].every(cb => cb.checked);
      });
   });
});

 
// Pagination
document.addEventListener("DOMContentLoaded", function () {
   const rowsPerPage = 12;
   let currentPage = 1;

   const tableBody = document.querySelector("tbody");
   const rows = Array.from(tableBody.querySelectorAll("tr"));
   const paginationContainer = document.querySelector(".pagination-numbers-container"); 
   const prevPage = document.getElementById("prevPage");
   const nextPage = document.getElementById("nextPage");

   function displayRows() {
      rows.forEach(row => row.style.display = "none");

      const startIndex = (currentPage - 1) * rowsPerPage;
      const endIndex = startIndex + rowsPerPage;
      rows.slice(startIndex, endIndex).forEach(row => row.style.display = "table-row");

      updatePagination();
   }

   function updatePagination() {
      paginationContainer.innerHTML = ""; 

      const totalPages = Math.ceil(rows.length / rowsPerPage);

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
      const totalPages = Math.ceil(rows.length / rowsPerPage);
      if (currentPage < totalPages) {
         currentPage++;
         displayRows();
      }
   });

   displayRows();
 });

// Modal 
document.addEventListener("DOMContentLoaded", function () {
   const actionButtons = document.querySelectorAll(".action-btn");
   const modalMessage = document.getElementById("modalMessage");
   const modalStatus = document.getElementById("modalStatus");
   const hiddenUserIds = document.getElementById("hiddenUserIds");
   const userCheckboxes = document.querySelectorAll("input[name='user_ids']");

   actionButtons.forEach(button => {
      button.addEventListener("click", function () {
         const status = button.getAttribute("data-status");
         modalMessage.innerText = `Are you sure you want to change the status of selected users to ${status}?`;
         modalStatus.value = status;

         hiddenUserIds.innerHTML = "";

         userCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
               let input = document.createElement("input");
               input.type = "hidden";
               input.name = "user_ids";
               input.value = checkbox.value;
               hiddenUserIds.appendChild(input);
            }
         });
      });
   });
});

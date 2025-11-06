$(document).ready(function () {
  $("#slider1, #slider2, #slider3").owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
      0: {
        items: 2,
        nav: false,
        autoplay: true,
      },
      600: {
        items: 4,
        nav: true,
        autoplay: true,
      },
      1000: {
        items: 6,
        nav: true,
        loop: true,
        autoplay: true,
      },
    },
  });

  $(document).on("click", ".plus-cart", function () {
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2];

    $.ajax({
      type: "GET",
      url: "/pluscart",
      data: {
        prod_id: id,
      },
      success: function (data) {
        eml.innerText = data.quantity;
        document.getElementById("amount").innerText = data.amount;
        document.getElementById("totalamount").innerText = data.totalamount;
      },
    });
  });

  $(document).on("click", ".minus-cart", function () {
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2];
    $.ajax({
      type: "GET",
      url: "/minuscart",
      data: {
        prod_id: id,
      },
      success: function (data) {
        eml.innerText = data.quantity;
        document.getElementById("amount").innerText = data.amount;
        document.getElementById("totalamount").innerText = data.totalamount;
      },
    });
  });

  $(document).on("click", ".remove-cart", function () {
    var id = $(this).attr("pid").toString();
    var eml = this;
    $.ajax({
      type: "GET",
      url: "/removecart",
      data: {
        prod_id: id,
      },
      success: function (data) {
        document.getElementById("amount").innerText = data.amount;
        document.getElementById("totalamount").innerText = data.totalamount;

        // Remove the item from DOM
        eml.parentNode.parentNode.parentNode.parentNode.remove();

        // Check if cart is now empty
        var cartContainer = document.getElementById("cart-items-container");
        if (cartContainer && cartContainer.children.length === 0) {
          // Hide the entire cart content and order summary
          var cartContentRow = document.getElementById("cart-content-row");
          var emptyCartTemplate = document.getElementById(
            "empty-cart-template"
          );

          if (cartContentRow) {
            cartContentRow.style.display = "none";
          }

          // Show empty cart message
          if (emptyCartTemplate) {
            emptyCartTemplate.classList.remove("d-none");
          }
        } else {
          // Update the cart items count badge
          var remainingItems = cartContainer
            ? cartContainer.children.length
            : 0;
          var cartBadge = document.getElementById("cart-items-badge");
          if (cartBadge && remainingItems > 0) {
            cartBadge.textContent =
              remainingItems + " Item" + (remainingItems > 1 ? "s" : "");
          }
        }
      },
    });
  });

  $(document).on("click", ".plus-wishlist", function () {
    var id = $(this).attr("pid").toString();
    $.ajax({
      type: "GET",
      url: "/pluswishlist",
      data: {
        prod_id: id,
      },
      success: function (data) {
        //alert(data.message)
        window.location.href = `http://localhost:8000/product-detail/${id}`;
      },
    });
  });

  $(document).on("click", ".minus-wishlist", function () {
    var id = $(this).attr("pid").toString();
    $.ajax({
      type: "GET",
      url: "/minuswishlist",
      data: {
        prod_id: id,
      },
      success: function (data) {
        window.location.href = `http://localhost:8000/product-detail/${id}`;
      },
    });
  });
});

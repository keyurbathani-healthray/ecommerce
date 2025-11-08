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
        document.getElementById("totalamount").innerText =
          data.totalamount.toFixed(2);

        // Update GST amounts
        document.getElementById("sgst").innerText =
          "Rs. " + data.sgst.toFixed(2);
        document.getElementById("cgst").innerText =
          "Rs. " + data.cgst.toFixed(2);

        // Update shipping amount display
        var shippingElement = document.getElementById("shipping");
        if (shippingElement) {
          if (data.shipping_amount === 0) {
            shippingElement.innerText = "FREE";
            shippingElement.className = "fw-semibold text-success";
          } else {
            shippingElement.innerText = "Rs. " + data.shipping_amount;
            shippingElement.className = "fw-semibold text-dark";
          }
        }

        // Update navbar cart badge
        var navbarCartBadge = document.getElementById("cart-badge");
        if (navbarCartBadge && data.cart_count !== undefined) {
          navbarCartBadge.childNodes[0].textContent = data.cart_count;
        }
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
        document.getElementById("totalamount").innerText =
          data.totalamount.toFixed(2);

        // Update GST amounts
        document.getElementById("sgst").innerText =
          "Rs. " + data.sgst.toFixed(2);
        document.getElementById("cgst").innerText =
          "Rs. " + data.cgst.toFixed(2);

        // Update shipping amount display
        var shippingElement = document.getElementById("shipping");
        if (shippingElement) {
          if (data.shipping_amount === 0) {
            shippingElement.innerText = "FREE";
            shippingElement.className = "fw-semibold text-success";
          } else {
            shippingElement.innerText = "Rs. " + data.shipping_amount;
            shippingElement.className = "fw-semibold text-dark";
          }
        }

        // Update navbar cart badge
        var navbarCartBadge = document.getElementById("cart-badge");
        if (navbarCartBadge && data.cart_count !== undefined) {
          navbarCartBadge.childNodes[0].textContent = data.cart_count;
        }
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
        document.getElementById("totalamount").innerText =
          data.totalamount.toFixed(2);

        // Update GST amounts
        document.getElementById("sgst").innerText =
          "Rs. " + data.sgst.toFixed(2);
        document.getElementById("cgst").innerText =
          "Rs. " + data.cgst.toFixed(2);

        // Update shipping amount display
        var shippingElement = document.getElementById("shipping");
        if (shippingElement) {
          if (data.shipping_amount === 0) {
            shippingElement.innerText = "FREE";
            shippingElement.className = "fw-semibold text-success";
          } else {
            shippingElement.innerText = "Rs. " + data.shipping_amount;
            shippingElement.className = "fw-semibold text-dark";
          }
        }

        // Update navbar cart badge
        var navbarCartBadge = document.getElementById("cart-badge");
        if (navbarCartBadge && data.cart_count !== undefined) {
          navbarCartBadge.childNodes[0].textContent = data.cart_count;
        }

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
    var button = $(this);
    $.ajax({
      type: "GET",
      url: "/pluswishlist",
      data: {
        prod_id: id,
      },
      success: function (data) {
        // Update navbar wishlist badge
        var wishlistBadge = document.getElementById("wishlist-badge");
        if (wishlistBadge && data.wishlist_count !== undefined) {
          wishlistBadge.childNodes[0].textContent = data.wishlist_count;
        }

        // Change button appearance
        button.removeClass("btn-outline-danger plus-wishlist");
        button.addClass("btn-danger minus-wishlist");
        button.html('<i class="fas fa-heart me-1"></i>Remove from Wishlist');
      },
    });
  });

  $(document).on("click", ".minus-wishlist", function () {
    var id = $(this).attr("pid").toString();
    var button = $(this);
    $.ajax({
      type: "GET",
      url: "/minuswishlist",
      data: {
        prod_id: id,
      },
      success: function (data) {
        // Update navbar wishlist badge
        var wishlistBadge = document.getElementById("wishlist-badge");
        if (wishlistBadge && data.wishlist_count !== undefined) {
          wishlistBadge.childNodes[0].textContent = data.wishlist_count;
        }

        // Change button appearance
        button.removeClass("btn-danger minus-wishlist");
        button.addClass("btn-outline-danger plus-wishlist");
        button.html('<i class="far fa-heart me-1"></i>Add to Wishlist');
      },
    });
  });

  $(document).on("click", ".remove-wishlist-btn", function (e) {
    e.preventDefault();
    var wishlistId = $(this).data("wishlist-id");
    var itemElement = $("#wishlist-item-" + wishlistId);

    $.ajax({
      type: "GET",
      url: "/remove_from_wishlist/" + wishlistId + "/",
      success: function (data) {
        if (data.success) {
          // Update navbar wishlist badge
          var wishlistBadge = document.getElementById("wishlist-badge");
          if (wishlistBadge && data.wishlist_count !== undefined) {
            wishlistBadge.childNodes[0].textContent = data.wishlist_count;
          }

          // Remove item with animation
          itemElement.fadeOut(300, function () {
            $(this).remove();

            // Check if wishlist is now empty
            if ($('[id^="wishlist-item-"]').length === 0) {
              // Reload page to show empty state
              location.reload();
            }
          });
        }
      },
      error: function () {
        alert("Error removing item from wishlist");
      },
    });
  });

  // ==================== SEARCH FUNCTIONALITY ====================

  var searchInput = $("#search-input");
  var searchForm = $("#search-form");
  var clearSearchTimeout;

  // Handle form submission
  searchForm.on("submit", function (e) {
    e.preventDefault();
    var query = searchInput.val().trim();

    if (query.length === 0) {
      // Redirect to home page if search is empty
      window.location.href = "/";
    } else {
      // Redirect to search results page with query
      window.location.href = "/search/?q=" + encodeURIComponent(query);
    }
    return false;
  });

  // Detect when search box is cleared (only on search results page)
  if (window.location.pathname === "/search/") {
    searchInput.on("input", function () {
      clearTimeout(clearSearchTimeout);
      var query = $(this).val().trim();

      // If search box is empty, redirect to home after a short delay
      if (query.length === 0) {
        clearSearchTimeout = setTimeout(function () {
          window.location.href = "/";
        }, 500); // 500ms delay
      }
    });
  }

  // ==================== END SEARCH FUNCTIONALITY ====================
});

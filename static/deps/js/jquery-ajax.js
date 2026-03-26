// adding to cart
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            let form = this.closest("form");
            let formData = new FormData(form);
            let button = this;

            if (button.classList.contains("processing")) {
                return;
            }

            button.classList.add("processing");

            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log("Server response:", data);

                    if (data.success) {
                        let cartCounter = document.querySelector("#goods-in-cart-count");
                        if (cartCounter) {
                            cartCounter.textContent = data.total_quantity || 0;
                        }

                        let cartContainer = document.querySelector("#cart-container");
                        if (cartContainer) {
                            cartContainer.innerHTML = data.cart_items_html;
                        }

                        showSuccessNotification("Product added to cart!");
                    } else {
                        showErrorNotification(data.message || "❌ Error adding product!");
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    showErrorNotification("❌ Server error! Try again");
                })
                .finally(() => {
                    setTimeout(() => button.classList.remove("processing"), 500);
                });
        });
    });
});

function updateCart(cartID, quantity, url) {
    $.ajax({
        type: "POST",
        url: url,
        data: {
            cart_id: cartID,
            quantity: quantity,
            csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (data) {
            $("#goods-in-cart-count").text(data.total_quantity || 0);
            $("#cart-items-container").html(data.cart_items_html);

            let price = data.total_price !== undefined ? data.total_price : "0,00";
            $("#total-cart-price").text(price + " UAH");
        },
        error: function () {
            showErrorNotification("Washing for a new cat");
        },
    });
}

// removing goods from the basket
$(document).on("click", ".remove-from-cart", function (e) {
    e.preventDefault();

    var cart_id = $(this).data("cart-id");
    var remove_from_cart = $(this).data("remove-url");
    var cartItemElement = $(this).closest(".cart-item");

    $.ajax({
        type: "POST",
        url: remove_from_cart,
        data: {
            cart_id: cart_id,
            csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (data) {
            $("#goods-in-cart-count").text(data.total_quantity || 0);

            cartItemElement.fadeOut(300, function () {
                $(this).remove();
            });

            $("#cart-items-container").html(data.cart_items_html);

            if (data.total_price !== undefined) {
                $("#total-cart-price").text(data.total_price + " UAH");
            }

            showSuccessNotification("The product has been removed from the cart!");
        },
        error: function () {
            showErrorNotification("❌ Error! Failed to delete item");
        }
    });
});

// types message
function alert_notification(message, type) {
    $("#jq-notification").remove();

    let $notify = $('<div id="jq-notification"></div>').appendTo('body');

    $notify.css({
        "position": "fixed",
        "top": "50%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
        "z-index": "99999", 
        "padding": "20px 30px",
        "border-radius": "5px", 
        "text-align": "center",
        "font-size": "18px",
        "font-weight": "bold",
        "min-width": "280px",
        "box-shadow": "0 10px 25px rgba(0,0,0,0.2)", 
        "display": "none"
    });

    if (type === "success") {
        $notify.css({ "background-color": "#bce5d5", "color": "#043724", "border": "1px solid #096740" });
    } else {
        $notify.css({ "background-color": "#f8d7da", "color": "#721c24", "border": "1px solid #f5c6cb" });
    }

    $notify.text(message);

    $notify.fadeIn(300).delay(2000).fadeOut(400, function () {
        $(this).remove();
    });
}

// Shortcut functions
function showSuccessNotification(message) {
    alert_notification(message, "success");
}

function showErrorNotification(message) {
    alert_notification(message, "error");
}

// + goods
$(document).on("click", ".decrement", function () {
    var url = $(this).data("cart-change-url");
    var cartID = $(this).data("cart-id");
    var $input = $(this).closest(".input-group").find(".number");
    var currentValue = parseInt($input.val());

    if (currentValue > 1) {
        var newQuantity = currentValue - 1;
        $input.val(newQuantity);
        updateCart(cartID, newQuantity, -1, url, $(this));
    }
});
// - goods
$(document).on("click", ".increment", function () {
    var url = $(this).data("cart-change-url");
    var cartID = $(this).data("cart-id");
    var $input = $(this).closest(".input-group").find(".number");
    var currentValue = parseInt($input.val());

    var newQuantity = currentValue + 1;
    $input.val(newQuantity);
    updateCart(cartID, newQuantity, 1, url, $(this));
});

 // Update the goods
function updateCart(cartID, quantity, change, url, button) {
    $.ajax({
        type: "POST",
        url: url,
        data: {
            cart_id: cartID,
            quantity: quantity,
            csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
        },

        success: function (data) {
            var successMessage = $("#success-message");
            successMessage.html(data.message).fadeIn(400);
            setTimeout(function () {
                successMessage.fadeOut(400);
            }, 7000);

            var goodsInCartCount = $("#goods-in-cart-count");
            var cartCount = parseInt(goodsInCartCount.text() || 0);
            cartCount += change;
            goodsInCartCount.text(cartCount);

            var productPriceElem = button.closest(".list-group-item").find(".cart-item-price");
            if (data.cart_price !== undefined) {
                productPriceElem.text(`Price: ${data.cart_price} UAH`);
            }

            $(".card-footer h4 strong").text(`${data.total_price} UAH`);

            $("#total-quantity").text(data.total_quantity);

            var productTotalElem = button.closest(".list-group-item").find(".cart-item-total-price");
            productTotalElem.text(`${data.product_total_price} UAH`);
        },
        error: function () {
            console.log("Error updating cart");
        },
    });
}

// delivery notification
var notification = $('#notification');
if (notification.length > 0) {
    setTimeout(function () {
        notification.alert('close');
    }, 7000);
}

$('#modalButton').click(function () {
    $('#exampleModal').appendTo('body');

    $('#exampleModal').modal('show');
});

$('#exampleModal .btn-close').click(function () {
    $('#exampleModal').modal('hide');
});

$("input[name='requires_delivery']").change(function () {
    var selectedValue = $(this).val();

    if (selectedValue === "1") {
        $("#deliveryAddressField").show();
    } else {
        $("#deliveryAddressField").hide();
    }
});

// phone number notification
document.getElementById('id_phone_number').addEventListener('input', function (e) {
    var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
    e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
});

$('#create_order_form').on('submit', function (event) {
    var phoneNumber = $('#id_phone_number').val();
    var regex = /^\(\d{3}\) \d{3}-\d{4}$/;

    if (!regex.test(phoneNumber)) {
        $('#phone_number_error').show();
        event.preventDefault();
    } else {
        $('#phone_number_error').hide();

        var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
        $('#id_phone_number').val(cleanedPhoneNumber);
    }
});

$(document).ready(function () {
    $(document).on('submit', '#search-form', function (e) {

        let query = $(this).find('input[name="q"]').val().trim();

        if (query === "") {
            e.preventDefault(); 
            showErrorNotification("Please enter a search query!");

            return false;
        }
    });
});

// login + photo notification
function createSocialNotify(provider) {
    const message = provider + " login will be available soon!";

    const notifyHtml = `
        <div id="temp-notify" class="alert alert-success alert-dismissible fade show custom-shadow" 
                role="alert"
                style="position: fixed; 
                    top: 85px; 
                    left: 50%; 
                    transform: translateX(-50%); 
                    z-index: 1000; 
                    min-width: 320px; 
                    text-align: center; 
                    border-radius: 5px;
                    background-color: #d1e7dd; 
                    border: 1px solid #badbcc; 
                    color: #0f5132;">
            <strong class="me-2">${message}</strong> 
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;

    const oldNotify = document.getElementById('temp-notify');
    if (oldNotify) oldNotify.remove();

    document.body.insertAdjacentHTML('afterbegin', notifyHtml);

    setTimeout(() => {
        const alert = document.getElementById('temp-notify');
        if (alert) {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }
    }, 3000);
}

document.getElementById('id_image').addEventListener('change', function () {
    const fileName = this.files[0] ? this.files[0].name : "No file chosen";
    document.getElementById('file-name').textContent = fileName;
});
function updateCart(itemId, action) {
    fetch(`/update_cart/${itemId}/${action}/`)
        .then(response => response.json())
        .then(data => location.reload());
}

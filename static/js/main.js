// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })

  // Shopping cart functionality
  const addToCartButtons = document.querySelectorAll('.add-to-cart')
  addToCartButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault()
      // Add to cart logic will be handled by Flask
      console.log('Add to cart clicked')
    })
  })

  // Search functionality
  const searchForm = document.querySelector('#search-form')
  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault()
      // Search logic will be handled by Flask
      console.log('Search submitted')
    })
  }

  // Wishlist toggle
  const wishlistButtons = document.querySelectorAll('.wishlist-toggle')
  wishlistButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault()
      // Wishlist logic will be handled by Flask
      console.log('Wishlist toggled')
    })
  })
})
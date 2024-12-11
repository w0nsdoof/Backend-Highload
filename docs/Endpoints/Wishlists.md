# Wishlist

## 1. Retrieve Wishlist
- **Request Type:** GET
- **Path:** `/api/wishlist/`
- **Description:** Retrieves all items in the user's wishlist.
- **Input:** No input required.
- **Output:**
  ```json
  {
    "id": 1,
    "wishlist_items": [
      {
        "id": 1,
        "product": { "id": 1, "name": "Cola 2l", "price": "800.00" }
      }
    ],
    "created_at": "2024-12-10T16:46:44Z",
    "updated_at": "2024-12-11T20:14:24Z"
  }
  ```

## 2. Add Item to Wishlist
- **Request Type:** POST
- **Path:** `/api/wishlist/add_item/`
- **Description:** Adds a product to the wishlist.
- **Input:**
  ```json
  {
    "product_id": 1
  }
  ```
- **Output:**
  ```json
  {
    "message": "Product added to wishlist."
  }
  ```

## 3. Remove Item from Wishlist
- **Request Type:** DELETE
- **Path:** `/api/wishlist/remove_item/`
- **Description:** Removes a product from the wishlist.
- **Input:**
  ```json
  {
    "product_id": 1
  }
  ```
- **Output:**
  ```json
  {
    "message": "Product removed from wishlist."
  }
  ```

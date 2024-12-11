# Carts

## 1. Create Cart
- **Request Type:** POST
- **Path:** `/api/carts/`
- **Description:** Creates an empty cart for the user if none exists. If a cart already exists, it will return the existing one.
- **Input:** No input required.
- **Output:**
  ```json
  {
    "id": 1,
    "user": 1,
    "cart_items": [],
    "total_items": 0,
    "total_price": 0,
    "created_at": "2024-12-10T16:41:33Z",
    "updated_at": "2024-12-10T16:45:16Z"
  }
  ```

## 2. Add Item
- **Request Type:** POST
- **Path:** `/api/carts/add_item/`
- **Description:** Adds an item to the cart.
- **Input:**
  ```json
  {
    "product_id": 1,
    "quantity": 2
  }
  ```
- **Output:**
  ```json
  {
    "id": 1,
    "product_id": 1,
    "quantity": 2,
    "subtotal": 1600
  }
  ```

## 3. Update Item
- **Request Type:** POST
- **Path:** `/api/carts/update_item/`
- **Description:** Updates a CartItem's quantity in the cart. If quantity is set to 0, the item will be removed.
- **Input:**
  ```json
  {
    "cart_item_id": 9,
    "quantity": 5
  }
  ```
- **Output:**
  ```json
  {
    "id": 9,
    "product_id": 1,
    "quantity": 5,
    "subtotal": 4000
  }
  ```

## 4. Delete Item
- **Request Type:** DELETE
- **Path:** `/api/carts/remove_item/`
- **Description:** Removes a CartItem from the cart by `cart_item_id`.
- **Input:**
  ```json
  {
    "cart_item_id": 9
  }
  ```
- **Output:**
  ```json
  {
    "message": "Item removed from cart."
  }
  ```


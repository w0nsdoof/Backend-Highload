# Review

## 1. Create Review
- **Request Type:** POST
- **Path:** `/api/products/{{product_id}}/reviews/`
- **Description:** Creates a review for a specific product. The review includes a rating and an optional comment.
- **Input:**
  ```json
  {
    "rating": 7,
    "comment": "Great product!"
  }
  ```
- **Output:**
  ```json
  {
    "id": 9,
    "product": 1,
    "user": 1,
    "rating": 7,
    "comment": "Great product!",
    "created_at": "2024-12-11T20:29:16Z"
  }
  ```

## 2. Retrieve Reviews
- **Request Type:** GET
- **Path:** `/api/products/{{product_id}}/reviews/`
- **Description:** Retrieves all reviews for a specific product.
- **Input:** No input required.
- **Output:**
  ```json
  [
    {
      "id": 9,
      "product": 1,
      "user": 1,
      "rating": 7,
      "comment": "Great product!",
      "created_at": "2024-12-11T20:29:16Z"
    }
  ]
  ```

## 3. Update Review
- **Request Type:** PUT
- **Path:** `/api/products/{{product_id}}/reviews/{{review_id}}/`
- **Description:** Updates an existing review for a product. You can modify the rating and the comment.
- **Input:**
  ```json
  {
    "rating": 8,
    "comment": "Updated review comment."
  }
  ```
- **Output:**
  ```json
  {
    "id": 9,
    "product": 1,
    "user": 1,
    "rating": 8,
    "comment": "Updated review comment.",
    "updated_at": "2024-12-11T20:45:16Z"
  }
  ```

## 4. Delete Review
- **Request Type:** DELETE
- **Path:** `/api/products/{{product_id}}/reviews/{{review_id}}/`
- **Description:** Deletes an existing review for a product.
- **Input:** No input required.
- **Output:**
  ```json
  {
    "message": "Review deleted successfully."
  }
  ```


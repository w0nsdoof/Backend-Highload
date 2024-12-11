### Authentication API Endpoints

#### Base URL: `/auth/`

1. **Login**

   - **Endpoint**: `POST /auth/login/`
   - **Description**: Authenticates a user and returns access and refresh tokens.
   - **Request Body**:
     ```json
     {
       "email": "user@example.com",
       "password": "password123"
     }
     ```
   - **Response Example**:
     ```json
     {
       "refresh": "<refresh_token>",
       "access": "<access_token>"
     }
     ```

2. **Register**

   - **Endpoint**: `POST /auth/register/`
   - **Description**: Registers a new user.
   - **Request Body**:
     ```json
     {
       "email": "user@example.com",
       "password": "password123",
       "username": "new_user"
     }
     ```
   - **Response Example**:
     ```json
     {
       "message": "User registered successfully!",
       "user": {
         "email": "user@example.com",
         "username": "new_user"
       }
     }
     ```

3. **Forgot Password**

   - **Endpoint**: `POST /auth/forgot_password/`
   - **Description**: Sends a password reset email to the user.
   - **Request Body**:
     ```json
     {
       "email": "user@example.com"
     }
     ```
   - **Response Example**:
     ```json
     {
        "message": "Password reset email sent."
     }
     ```
4. **Reset Password**
   - **Endpoint**: `POST /auth/reset_password/<uid>/<token>`
   - **Description**: A link from email from forgot password method
   - **Request Body**:
     ```json
     {
       "password": "GENERATE_RANDOM" // Generates random password sent in email
       // Could be custom one that is not == GENERATE_RANDOM
     }
     ```
   - **Response Example**:
     ```json
     {
        "message": "Password reset successful."
     }
     ```
   - **Response in Email if GENERATE_RANDOM**:
     ```
     Your new password is: 5VHsMAKG 
     ```

# References
- https://www.geeksforgeeks.org/otp-verification-in-django-rest-framework-using-jwt-and-cryptography/?ref=ml_lbp


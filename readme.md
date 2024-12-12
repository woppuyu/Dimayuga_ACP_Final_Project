# Classroom Connect: School Supplies Donation System

## Project Overview
Classroom Connect is a desktop application designed to facilitate the donation and management of school supplies. The system helps bridge the gap between donors and students in need by providing an efficient platform for tracking donations, managing inventory, and coordinating supply distribution.

This project aligns with UN Sustainable Development Goal 4 (Quality Education) by addressing the basic needs of students who lack essential school supplies, thereby supporting their educational journey.

## Technical Implementation

### Python Concepts Applied
- **Object-Oriented Programming (OOP)**
  - Class inheritance and composition
  - Encapsulation of database operations
  - Event-driven programming with GUI elements

- **Error Handling**
  - Try-except blocks for database operations
  - Input validation and data sanitization
  - Graceful error messaging to users

- **Database Management**
  - MySQL connection and CRUD operations
  - Transaction management
  - Parameterized queries for security

### Libraries Used
1. **customtkinter**
   - Modern GUI framework
   - Themed widgets and responsive design
   - Dark mode support

2. **mysql-connector-python**
   - Database connectivity
   - Secure query execution
   - Connection pooling

3. **tkinter/ttk**
   - Treeview for data display
   - Scrollbars and native widgets
   - Event handling

4. **CTkMessagebox**
   - User notifications
   - Error messages
   - Confirmation dialogs

## SDG Integration - Quality Education (SDG 4)

### Overview
This project directly supports the United Nations Sustainable Development Goal 4 (Quality Education), which aims to "ensure inclusive and equitable quality education and promote lifelong learning opportunities for all." By facilitating the donation and distribution of school supplies, we address one of the fundamental barriers to education: lack of basic learning materials.

### Key SDG 4 Targets Addressed

1. **Target 4.1** - Free, equitable, and quality education
   - Ensures students have necessary supplies for learning
   - Reduces financial burden on families
   - Supports equal access to educational resources

2. **Target 4.5** - Equal access to education
   - Eliminates gender disparities in access to supplies
   - Supports vulnerable populations
   - Reduces economic barriers to education

### Impact Areas

1. **Resource Distribution**
   - Systematic tracking of donations
   - Efficient allocation of supplies
   - Need-based distribution system
   - Inventory management for sustainability

2. **Community Engagement**
   - Connects donors with educational needs
   - Promotes community participation
   - Builds awareness of educational challenges
   - Encourages ongoing support

3. **Educational Support**
   - Ensures basic learning materials availability
   - Supports classroom participation
   - Enhances learning experience
   - Reduces student dropout rates

4. **Long-term Sustainability**
   - Continuous donation tracking
   - Regular supply monitoring
   - Data-driven distribution
   - Transparent resource management

### Measurable Outcomes
1. Number of students supported
2. Quantity of supplies distributed
3. Donor participation rates
4. Supply availability metrics
5. Distribution efficiency statistics

This system not only provides immediate relief through supply distribution but also creates a sustainable framework for ongoing educational support, directly contributing to the achievement of SDG 4's broader goals.

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server

### Database Setup

#### Prerequisites
- MySQL Server installed (XAMPP/WAMP/standalone MySQL)
- phpMyAdmin or MySQL Workbench (for GUI management)
- Basic understanding of database operations

#### Detailed Setup Steps

1. **Start MySQL Server**
   - If using XAMPP: Start Apache and MySQL modules
   - If using WAMP: Start all services
   - If using standalone MySQL: Ensure service is running

2. **Access Database Management Tool**
   - For phpMyAdmin: 
     - Open browser and navigate to `http://localhost/phpmyadmin`
     - Login with your credentials (default user: 'root', no password)
   - For MySQL Workbench:
     - Open MySQL Workbench
     - Connect to your local instance

3. **Create Database**
   ```sql
   CREATE DATABASE schoolsuppliesdonationdb;
   ```
   Or using GUI:
   - Click "New" in phpMyAdmin
   - Enter "schoolsuppliesdonationdb" as database name
   - Select "utf8mb4_general_ci" as collation
   - Click "Create"

4. **Import Schema**
   - Select the newly created database
   - Go to "Import" tab
   - Choose `schoolsuppliesdonationdb.sql` file
   - Click "Go" or "Import"

5. **Verify Installation**
   - Check if these tables exist:
     - supplies
     - donations
     - withdrawals
   - Verify initial supply items are loaded
   - Check foreign key constraints

6. **Configure Application Connection**
   Default credentials in application.py:
   ```python
   host="localhost"
   user="root"
   password=""
   database="schoolsuppliesdonationdb"
   ```
   Modify these if your setup differs.

7. **Admin Credentials Setup**
   The default admin credentials are stored directly in the application.py code:
   ```python
   ADMIN_USERNAME = "admin"
   ADMIN_PASSWORD = "admin123"
   ```
   For security purposes, you should modify these credentials by changing them directly in the code before deploying the application.
   
   Current default login:
   - Username: admin
   - Password: admin123

8. **Troubleshooting**
   - Ensure MySQL server is running on port 3306
   - Check if user has proper privileges
   - Verify database name matches exactly
   - Confirm character set is utf8mb4

### Installation Steps
1. Download the project files:
   - Download `application.py` (Main application)
   - Download `schoolsuppliesdonationdb.sql` (Database schema)

2. Place all files in a directory of your choice

3. Install required packages:
```bash
pip install customtkinter
pip install mysql-connector-python
pip install CTkMessagebox
```

4. Set up the database:
   - Open MySQL/phpMyAdmin
   - Create a new database named `schoolsuppliesdonationdb`
   - Import the `schoolsuppliesdonationdb.sql` file

5. Run the application:
```bash
python application.py
```

## Features

### 1. Donation Management
- Easy-to-use donation form
- Automatic inventory updates
- Contact information validation
- Location tracking

### 2. Inventory Tracking
- Real-time supply quantities
- Categorized supply items
- Low stock alerts
- Historical data tracking

### 3. Admin Dashboard
- Secure login system
- Comprehensive donation records
- Withdrawal management
- Transaction history

### 4. Supply Distribution
- Controlled withdrawal system
- Record keeping
- Supply availability checks
- Distribution tracking

## Usage Guide

### For Donors
1. Launch the application
2. Click "Add Donation"
3. Fill in personal details
4. Select supplies and quantities
5. Submit donation

### For Administrators
1. Access admin panel via login
2. View current inventory
3. Process withdrawals
4. Monitor donation records
5. Track supply distribution

## Security Features
- Secure admin authentication
- Input validation
- SQL injection prevention
- Error handling

## Project Structure
```
ACP_Project/
├── application.py                  # Main application file
├── schoolsuppliesdonationdb.sql    # Database schema
└── readme.md                       # Documentation
```

## Database Schema

### Tables
1. **supplies**
   - id (Primary Key)
   - supply_name
   - quantity

2. **donations**
   - id (Primary Key)
   - donor_name
   - contact_info
   - address
   - supply_id (Foreign Key)
   - quantity
   - donation_date

3. **withdrawals**
   - id (Primary Key)
   - supply_id (Foreign Key)
   - quantity
   - withdrawal_date

## License
This project is licensed under the MIT License.
# RentHive

RentHive is a modern property management platform designed for the Kenyan rental market. It streamlines the relationship between property owners and tenants, offering digital onboarding, automated lease management, integrated payments (Mpesa, card, bank), maintenance tracking, and real-time messaging—all within a user-friendly, mobile-responsive interface.

## Features

- **Owner & Tenant Onboarding:** Guided registration and onboarding flows for both owners and tenants, including invite-based tenant registration.
- **Property & Unit Management:** Owners can add properties and units, invite tenants, and view detailed statistics.
- **Automated Lease Creation:** Leases are automatically created when tenants register via an invite, with manual management available for admins.
- **Digital Payments:** Supports Mpesa (Daraja API), card, and bank payments, with real-time rent status updates for owners and tenants.
- **Maintenance Requests:** Tenants can submit and track maintenance requests; owners can export reports and manage requests efficiently.
- **Messaging System:** Secure, chat-style messaging between owners and tenants, with inboxes and conversation history.
- **Password Reset & Security:** Secure authentication, password reset via email, and role-based access control.
- **Modern UI:** Built with Tailwind CSS for a clean, responsive, and accessible user experience.

## System Requirements

- Python 3.11+
- Django 5.2+
- PostgreSQL (or SQLite for development)
- Mpesa Daraja API credentials (for live payments)
- Email backend (for password reset and notifications)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/RentHiveDev.git
   cd RentHiveDev
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv renthive_env
   renthive_env\Scripts\activate  # On Windows
   # Or
   source renthive_env/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and set your database, email, and Mpesa credentials.
5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Create a superuser:**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```
8. **Access the app:**
   - Visit `http://127.0.0.1:8000/` in your browser.

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Django Project
- Safaricom Daraja API
- Tailwind CSS
- All contributors and testers

---

For more information, see the in-app documentation or contact the project maintainer.
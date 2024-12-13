# auto-email-notifications
A Python script that automatically generates and sends a daily email at 8 AM with a graph displaying the company's daily charge variation. It connects to a PostgreSQL database, creates the graph using Matplotlib, and sends the email via SMTP

## Installation

Once you have cloned the repository, follow these steps to install the dependencies and set up the project:

1. **Clone the repository:**
   If you haven't cloned the repository yet, run:
   ```bash
   git clone https://github.com/J-Marroquin/auto-email-notifications.git
   
2. **Navigate to the project directory**:  
   `cd your-directory-name`

3. **Install dependencies using `pipenv`**: It's recommended to use `pipenv` for managing dependencies. To install all dependencies listed in the `Pipfile`, run:  
   `pipenv install`

4. **Activate the virtual environment**: Once the dependencies are installed, activate the virtual environment with:  
   `pipenv shell`

5. **Generate the executable**:  
   To create the standalone executable, run the following command:
   ```bash  
   pyinstaller --onefile --add-data "config.ini:." --hidden-import ReportGenerator --hidden-import Logger --hidden-import EmailSender --name "Company.Reports" Program.py
   ```
   This command will generate an executable named `Company.Reports` in the `dist` folder.

7. **Use the executable**:  
   Once the executable is generated, copy the `config.ini` file to the same directory as the executable. After that, you can run the executable directly without needing a Python environment.


This will execute the script that generates and sends the email with the graph.

## Configuration

For the project to work, you need to create a `config.ini` file containing the necessary credentials. 

1. **Create a new file named `config.ini`**:

2. **Configure the necessary credentials**:
   Open the `config.ini` file and replace the placeholders with your actual credentials.

   The structure of the `config.ini` file should look like this:

   ```ini
   [PRODUCTION]
   DB_SERVER = your-database-host
   DB_PORT = 5432
   DB_NAME = your-database-name
   DB_USER = your-database-user
   DB_PASSWORD = your-database-password
   TO = PrimaryRecipient@example.com , Recipient2@example.com , Recipient3@example.com.mx
   
   [SMTP]
   SMTP_SERVER = smtp.your-email-provider.com
   SMT_PORT = 587
   EMAL_ADDRESS = your-email@example.com
   EMAIL_PASSWORD = your-email-password

## Scheduling the Script

To run the script automatically every day at 8 AM, you need to create a scheduled task. Below are the instructions for setting up the task on **Windows**.

### Windows (Task Scheduler)

1. **Open Task Scheduler**:
   - Press `Windows + R`, type `taskschd.msc` and press `Enter` to open the Task Scheduler.

2. **Create a new task**:
   - In the Task Scheduler window, click on **Create Basic Task** in the right-hand pane.

3. **Set the task name**:
   - Give your task a name (e.g., "Daily Report Email").

4. **Set the trigger**:
   - Choose the **Daily** option and set the time to 8:00 AM. Click **Next**.

5. **Set the action**:
   - Choose **Start a Program**.
   - Click **Browse** and navigate to the location of your executable (e.g., `Company.Reports.exe`).
   - Select the executable and click **Next**.

6. **Finish the task setup**:
   - Review the task settings and click **Finish** to create the scheduled task.

Now, your executable will run automatically every day at 8 AM.
   

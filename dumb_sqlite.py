import subprocess

# Function to export data with UTF-8 encoding


def export_data():
    with open('data.json', 'w', encoding='utf-8') as f:
        subprocess.run(['python', 'manage.py', 'dumpdata',
                       '--natural-primary', '--natural-foreign'], stdout=f, check=True)

# Main function to handle the export


def create_json_dump():
    print("Exporting data from SQLite...")
    export_data()
    print("Data export completed successfully.")


if __name__ == '__main__':
    create_json_dump()

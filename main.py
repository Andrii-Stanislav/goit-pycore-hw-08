from collections import UserDict
from datetime import datetime, timedelta

class ValidationException(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate_name(value)

    def validate_name(self, value):
        if not value.isalpha():
            raise ValidationException("Name must contain only letters")

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate_phone(value)

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValidationException("Phone number must be 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValidationException("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        
        
    def show_birthday(self):
        if self.birthday:
            return self.birthday.value.strftime("%d.%m.%Y")
        return "Birthday not set"

    def __str__(self):
        birthday_str = f", birthday: {self.show_birthday()}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if not record.birthday:
                continue
                        
            birthday = record.birthday.value            

            this_year_birthday = birthday.replace(year=today.year)

            # If birthday is in the past, move it to next year
            if this_year_birthday < today:
                this_year_birthday = this_year_birthday.replace(year=today.year + 1)

            # Check if birthday is in the next 7 days
            if 0 <= (this_year_birthday - today).days <= 7:
                congratulation_date = this_year_birthday

                # If birthday is on Saturday or Sunday, move it to Monday
                if congratulation_date.weekday() == 5:  # Sateday
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Sunday
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y"),
                    "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                })
                
        return upcoming_birthdays

    def add_contact(self, name, phone=None):
        record = self.find(name)
        if record is None:
            record = Record(name)
            self.add_record(record)
            message = "Contact added."
        else:
            message = "Contact updated."
        if phone:
            record.add_phone(phone)
        return message

    def change_contact(self, name, old_phone, new_phone):
        record = self.find(name)
        if record is None:
            raise KeyError('Contact not found.')
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."

    def show_phone(self, name):
        record = self.find(name)
        if record is None:
            raise KeyError('Contact not found.')
        return '; '.join(phone.value for phone in record.phones)

    def show_all(self):
        if not self.data:
            return "No contacts available."
        return '\n'.join(str(record) for record in self.data.values())

# ! Decorators

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

# ! Handlers

@input_error
def handle_add_birthday(args, book):
    if len(args) != 2:
        raise IndexError('Please provide contact name and birthday date.')
    print('args: ', args)

    name, date = args
    record = book.find(name)
    if not record:
        raise KeyError('Contact not found.')
    record.add_birthday(date)
    return "Birthday added"

@input_error
def handle_show_birthday(args, book):
    if len(args) != 1:
        raise IndexError('Please provide contact name.')
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError('Contact not found.')
    return record.show_birthday()

@input_error
def handle_birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if len(upcoming) == 0:
        return "There are no birthdays in the next 7 days."
    result = []
    for birthday in upcoming:
        result.append(f"{birthday['name']}: birthday on {birthday['birthday']}, celebrate on {birthday['congratulation_date']}")
    return "\n".join(result)

@input_error
def handle_add_contact(args, book):
    print('args: ', args)
    if len(args) != 2:
        raise IndexError('Please provide contact name and phone number.')
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    return book.add_contact(name, phone)

@input_error
def handle_change_contact(args, book):
    if len(args) != 3:
        raise IndexError('Please provide contact name, old phone number and new phone number.')
    name, old_phone, new_phone = args
    return book.change_contact(name, old_phone, new_phone)

@input_error
def handle_show_phone(args, book):
    if len(args) != 1:
        raise IndexError('Please provide contact name.')
    name = args[0]
    return book.show_phone(name)

@input_error
def handle_show_all(book):
    return book.show_all()

def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    args = [arg.strip() for arg in args]  # Clean up each argument
    return cmd, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if not command:
            print("Please enter a command")
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(handle_add_contact(args, book))
        elif command == "change":
            print(handle_change_contact(args, book))
        elif command == "phone":
            print(handle_show_phone(args, book))
        elif command == "all":
            print(handle_show_all(book))
        elif command == "add-birthday":
            print(handle_add_birthday(args, book))
        elif command == "show-birthday":
            print(handle_show_birthday(args, book))
        elif command == "birthdays":
            print(handle_birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

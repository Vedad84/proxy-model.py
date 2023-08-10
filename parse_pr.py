import sys

def parse_description(description):
    lines = description.split("\n")
    fields = { "Sprint": "", "Environment": "", "Date": "", "Tickets": "", "Significant Updates": "", "Bug Fixes": "" }

    current_field = None
    for line in lines:
        if ":" in line:
            field, value = line.split(":", 1)
            if field in fields:
                current_field = field
                fields[field] = value.strip()
            else:
                current_field = None
        elif current_field:
            fields[current_field] += "\n" + line.strip()

    return fields

def format_changelog_entry(fields):
    return "\n".join(f"{field}: {value}" for field, value in fields.items())

description = sys.stdin.read()
fields = parse_description(description)
print(format_changelog_entry(fields))

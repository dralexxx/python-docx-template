from .template import DocxTemplate,TemplateError
import argparse, json
from pathlib import Path
from argparse import ArgumentError


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage='docxtpl template_path json_path output_filename',
        description='Make docx file from existing template docx and json data.')
    parser.add_argument('Template',
                        metavar='template_path',
                        type=str,
                        help='The path to the template docx file.')
    parser.add_argument('Json',
                        metavar='json_path',
                        type=str,
                        help='The path to the json file with the data.')
    parser.add_argument('Output',
                        metavar='output_filename',
                        type=str,
                        help='The filename to save the generated docx.')
    return parser


def get_args(parser: argparse.ArgumentParser) -> dict:
    try:
        parsed_args = vars(parser.parse_args())
        return parsed_args
    # Argument errors cause SystemExit error, not ArgumentError
    except SystemExit:
        raise RuntimeError(f'Correct usage is:\n{parser.usage}')


def is_argument_valid(arg_name: str, arg_value: str) -> bool:
    if arg_name == 'Template':
        return Path(arg_value).is_file() and arg_value.endswith('.docx')
    elif arg_name == 'Json':
        return Path(arg_value).is_file() and arg_value.endswith('.json')
    elif arg_name == 'Output':
        return arg_value.endswith('.docx') and check_exists_ask_overwrite(
            arg_value)


def check_exists_ask_overwrite(arg_value) -> bool:
    if Path(arg_value).exists():
        try:
            if input(f'File {arg_value} already exists, would you like to overwrite the existing file? (y/n)').lower() == 'y':
                return True
            else:
                raise FileExistsError
        except FileExistsError as e:
            raise RuntimeError(f'File {arg_value} already exists, please choose a different name.') from e
    else:
        return True


def validate_all_args(parsed_args) -> None:
    try:
        for arg_name, arg_value in parsed_args.items():
            if not is_argument_valid(arg_name, arg_value):
                raise ArgumentError
    except ArgumentError as e:
        raise RuntimeError(
            f'The specified {arg_name} "{arg_value}" is not valid.')


def get_json_data(json_path: Path) -> dict:
    with open(json_path) as file:
        try:
            json_data = json.load(file)
            return json_data
        except json.JSONDecodeError as e:
            print(
                f'There was an error on line {e.lineno}, column {e.colno} while trying to parse file {json_path}')
            raise RuntimeError('Failed to get json data.')


def make_docxtemplate(template_path: Path) -> DocxTemplate:
    try:
        return DocxTemplate(template_path)
    except TemplateError as e:
        raise RuntimeError('Could not create docx template.') from e


def save_file(doc: DocxTemplate, output_path: Path) -> None:
    try:
        doc.save(output_path)
        print(f'Document successfully generated and saved at {output_path}')
    except PermissionError as e:
        print(f'{e.strerror}. Could not save file {e.filename}.')
        raise RuntimeError('Failed to save file.') from e


def main() -> None:
    parser = make_arg_parser()
    try:
        parsed_args = get_args(parser)
        validate_all_args(parsed_args)
        json_data = get_json_data(Path(parsed_args['Json']).resolve())
        doc = make_docxtemplate(Path(parsed_args['Template']).resolve())
        doc.render(json_data)
        save_file(doc, Path(parsed_args['Output']).resolve())
    except RuntimeError as e:
        print(e)
        return
    finally:
        print('Exiting program!')


if __name__ == '__main__':
    main()
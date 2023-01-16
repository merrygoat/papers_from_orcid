import yaml
import orcid
from thefuzz import fuzz


def main():
    output_path = "output.txt"
    credentials_path = "credentials.yaml"
    orcids_path = "orcids.txt"
    publication_year = 2020

    credentials = get_credentials(credentials_path)
    api = orcid.PublicAPI(credentials["client_id"], credentials["client_secret"])
    token = api.get_search_token_from_orcid()
    orcids = read_orcids(orcids_path)
    write_output_header(output_path, publication_year)

    for identifier in orcids:
        record = api.read_record_public(identifier, 'record', token)
        works = api.read_record_public(identifier, 'works', token)["group"]
        works = filter_works_by_date(works, publication_year)
        works = remove_duplicates(works)
        output_works(works, record, output_path)


def write_output_header(output_path: str, publication_year: int):
    with open(output_path, 'w') as output_file:
        output_file.write(f"List of publications from selected ORCIDS from https://orcid.org/ "
                          f"since 01/01/{publication_year}\n\n")


def read_orcids(file_name: str) -> list[str]:
    with open(file_name, 'r') as input_file:
        orcids = input_file.readlines()
    orcids = [identifier.strip() for identifier in orcids]
    return orcids


def filter_works_by_date(works: list[dict], year: int) -> list[dict]:
    filtered_works = []
    for work in works:
        if int(work["work-summary"][0]["publication-date"]["year"]["value"]) >= year:
            filtered_works.append(work)
    return filtered_works


def remove_duplicates(works: list[dict]) -> list[dict]:
    filtered_works = []
    while works:
        work = works.pop()
        distances = [fuzz.ratio(work["work-summary"][0]["title"]["title"]["value"],
                                other_work["work-summary"][0]["title"]["title"]["value"]) for other_work in works]
        if not distances or max(distances) < 90:
            filtered_works.append(work)
    return filtered_works


def output_works(works: list[dict], record: dict, output_path: str):
    with open(output_path, 'a') as output_file:
        name = f'{record["person"]["name"]["given-names"]["value"]} {record["person"]["name"]["family-name"]["value"]}'
        identifier = record["orcid-identifier"]["uri"]
        output_file.write(f"{name} - {identifier}\n")
    work_titles = []
    for work in works:
        title = work["work-summary"][0]["title"]["title"]["value"]
        year = work["work-summary"][0]["publication-date"]["year"]["value"]
        work_titles.append(f"{title} - {year}")
    with open(output_path, 'a') as output_file:
        for title in work_titles:
            output_file.write(f"{title}\n")
        output_file.write("\n")


def get_credentials(file_name: str):
    with open(file_name, 'r') as input_file:
        credential_list = ["client_id", "client_secret"]
        credentials = yaml.safe_load(input_file)
        for item in credential_list:
            if item not in credentials:
                raise SyntaxError(f"No '{item}' found in {file_name}.")
        return credentials


if __name__ == "__main__":
    main()

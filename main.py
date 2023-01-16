import yaml
import orcid


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
        works = api.read_record_public(identifier, 'works', token)
        output_works(works, record, output_path)


def write_output_header(output_path: str, publication_year: int):
    with open(output_path, 'w') as output_file:
        output_file.write(f"List of publications from orcids since 01/01/{publication_year}\n\n")


def read_orcids(file_name: str) -> list[str]:
    with open(file_name, 'r') as input_file:
        orcids = input_file.readlines()
    orcids = [identifier.strip() for identifier in orcids]
    return orcids


def output_works(works: dict, record: dict, output_path: str):
    with open(output_path, 'a') as output_file:
        name = f'{record["person"]["name"]["given-names"]["value"]} {record["person"]["name"]["family-name"]["value"]}'
        identifier = record["orcid-identifier"]["uri"]
        output_file.write(f"{name} - {identifier}\n")
    work_titles = []
    for work in works["group"]:
        work_summary = work["work-summary"][0]
        if int(work_summary["publication-date"]["year"]["value"]) >= 2020:
            work_titles.append(work_summary["title"]["title"]["value"])
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

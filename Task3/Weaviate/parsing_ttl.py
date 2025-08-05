import json
import re
import os
from pathlib import Path


def parse_ttl_to_json(ttl_content, file_id=None):
    entities = {}

    lines = [line.strip() for line in ttl_content.split('\n')
             if line.strip() and not line.strip().startswith(('@prefix', '#'))]

    full_text = '\n'.join(lines)
    records = []
    current_record = []
    in_quotes = False

    for line in full_text.split('\n'):
        if not line.strip():
            continue

        quote_count = line.count('"')
        if quote_count % 2 != 0:
            in_quotes = not in_quotes

        current_record.append(line)

        if line.rstrip().endswith('.') and not in_quotes:
            records.append(' '.join(current_record))
            current_record = []

    for record in records:
        subject_match = re.match(r'^:?([^\s]+)', record)
        if not subject_match:
            continue
        entity_id = subject_match.group(1).replace('_', ' ')

        type_match = re.search(r'rdf:type\s+comcore:(\w+)', record)
        entity_type = type_match.group(1) if type_match else 'Unknown'

        label_match = re.search(r'rdfs:label\s+"([^"]+)"@?ru?', record)
        label = label_match.group(1) if label_match else entity_id

        abbrev_matches = re.findall(r'comcore:abbreviation\s+"([^"]+)"', record)
        abbreviations = list(set(abbrev_matches)) if abbrev_matches else []  # Удаляем дубликаты

        definition_match = re.search(r'dc:definition\s+"((?:[^"\\]|\\.)*)"', record)
        definition = definition_match.group(1) if definition_match else ""

        mentioned_in_match = re.search(r'comcore:mentionedIn\s+:(\d+)', record)
        chunk_id = mentioned_in_match.group(1) if mentioned_in_match else file_id
        chunk_id = str(int(chunk_id)) if chunk_id and chunk_id.isdigit() else chunk_id

        if entity_id not in entities:
            entities[entity_id] = {
                "label": label,
                "abbreviation": abbreviations,  # Теперь это всегда список
                "definition": definition,
                "type": entity_type,
                "hasStatement": [],
                "chunk_id": chunk_id
            }
        else:
            if label:
                entities[entity_id]["label"] = label
            if entity_type != 'Unknown':
                entities[entity_id]["type"] = entity_type
            if abbreviations:
                # Объединяем с существующими аббревиатурами, удаляем дубли
                existing = set(entities[entity_id]["abbreviation"])
                new = set(abbreviations)
                entities[entity_id]["abbreviation"] = list(existing.union(new))
            if definition:
                entities[entity_id]["definition"] = definition
            if chunk_id:
                entities[entity_id]["chunk_id"] = chunk_id

        relations = re.finditer(r'(comcore:(?!mentionedIn)(\w+))\s+:([^\s;,.]+)', record)
        for match in relations:
            rel_type = match.group(2)
            target = match.group(3).replace('_', ' ')

            stmt = f"{entity_id} {rel_type} {target}"
            entities[entity_id]["hasStatement"].append(stmt)

            reverse_relations = {
                'hasPart': 'isPartOf',
                'isPartOf': 'hasPart',
                'isActorOf': 'hasActor',
                'hasActor': 'isActorOf',
                'isResourceOf': 'hasResource',
                'hasResource': 'isResourceOf',
                'isResultOf': 'hasResult',
                'hasResult': 'isResultOf',
                'isResponsibleFor': 'hasResponsible',
                'hasResponsible': 'isResponsibleFor',
                'relation': 'relation'
            }

            if rel_type in reverse_relations:
                reverse_stmt = f"{target} {reverse_relations[rel_type]} {entity_id}"
                if target not in entities:
                    entities[target] = {
                        "label": target,
                        "abbreviation": [],
                        "definition": "",
                        "type": "Unknown",
                        "hasStatement": [reverse_stmt],
                        "chunk_id": chunk_id or file_id
                    }
                else:
                    entities[target]["hasStatement"].append(reverse_stmt)

    return list(entities.values())


def process_all_ttl_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for ttl_file in Path(input_dir).glob('*.ttl'):
        file_id = ttl_file.stem.split('_')[-1]
        file_id = str(int(file_id)) if file_id.isdigit() else file_id

        with open(ttl_file, 'r', encoding='utf-8') as f:
            ttl_content = f.read()

        json_data = parse_ttl_to_json(ttl_content, file_id)

        output_file = Path(output_dir) / f"triplet_{file_id}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"Обработан: {ttl_file} -> {output_file}")


if __name__ == "__main__":
    input_dir = 'C:/Users/MSI/PycharmProjects/PythonProject/triplets/triplets2'
    output_dir = 'C:/Users/MSI/PycharmProjects/PythonProject/json_triplets/json_triplets2'
    process_all_ttl_files(input_dir, output_dir)
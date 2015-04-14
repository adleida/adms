import yaml

with open('./main.yaml', 'r') as f:
    etc = yaml.load(f.read())
print etc

import yaml
import jinja2
import click
from pathlib import Path

EXPERIMENT_TEMPLATE = 'experiment.yml.j2'
JINJA2_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('.'), variable_start_string='<<<',
    variable_end_string='>>>')

def __load_yaml(file: Path):
    with open(file) as f:
        return yaml.safe_load(f)


def __resolve_host(task: dict, host: str) -> list:
    if host == 'all':
        return [task]
    else:
        hosts = host.strip().split(',')
        tasks = []
        for h in hosts:
            # task['delegate_to'] = h
            # task['run_once'] = True
            if 'when' in task:
                task['when'] = [
                    task['when'],
                    f"inventory_hostname == '{h}'"
                ]
            else:
                task['when'] = f"inventory_hostname == '{h}'"
            tasks.append(task.copy())
        return tasks

def __resolve_include_tasks(task: dict):
    if 'include_tasks' in task:
        include_tasks_file = task.pop('include_tasks')
        variables = task.pop('vars')
        template = JINJA2_ENV.get_template(include_tasks_file)
        rendered = template.render(variables)
        tasks_list = yaml.safe_load(rendered)
        tasks = []
        for new_task in tasks_list:
            if 'when' in new_task:
                new_task['when'] = [
                    new_task['when'],
                    task['when'],
                ]
            else:
                if 'when' in task:
                    new_task['when'] = task['when']
            tasks.append(new_task.copy())
        return tasks
    return [task]

def __transform_task(task: dict) -> list:
    single = task.get('task', False)
    host = task.get('host', 'localhost')

    if single:
        tasks = __resolve_host(task['task'], host)
        new_tasks = [x for t in tasks for x in __resolve_include_tasks(t)]
        return new_tasks
    else:
        tasks = [__resolve_host(t, host) for t in task['tasks']]
        new_tasks = [y for t in tasks for x in t for y in __resolve_include_tasks(x)]
        return new_tasks


def load_tasks(task_type: str, experiment_config: dict, file: Path) -> list:
    tasks = []
    if task_type in experiment_config:
        for name in experiment_config[task_type]:
            task_file = Path(file).parent / name
            task_list = __load_yaml(task_file)['tasks']
            for t in task_list:
                tasks.extend(__transform_task(t))
    return tasks

def indent_yaml(yaml_str, spaces=4):
    """
    Indent every line of the given YAML string by the specified number of spaces.
    """
    indentation = ' ' * spaces
    return '\n'.join(f'{indentation}{line}' if line.strip() else line for line in yaml_str.splitlines())

def run_ansible(file: Path):
    import subprocess
    import sys

    playbook_path = file.relative_to('.').as_posix()

    # Use subprocess.Popen for real-time output
    process = subprocess.Popen(
    ['./ansible-playbook.sh', playbook_path],
        stdout=sys.stdout,  # Stream to console in real-time
        stderr=sys.stderr
    )

    # Wait for the process to complete
    process.communicate()

    # Return code
    print(f"\nAnsible exited with return code: {process.returncode}")


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--pattern', default='*.yml', help='Glob pattern to match files (default: *.yml)')
@click.option('--prevent_clean', is_flag=True, help='Do not remove rendered files after processing')
def main(path: Path, pattern: str, prevent_clean: bool):
    """
    Process a YAML experiment file or all matching files in a directory.
    """

    # If it's a file, make it a list with one file
    if path.is_file():
        files = [path]
    else:
        # If it's a directory, apply glob pattern
        files = sorted(path.glob(pattern))
        # sort out all files starting with x
        files = [file for file in files if not file.name.startswith('x')]

    if not files:
        click.echo(f"No files found in {path} matching pattern '{pattern}'")
        return

    for file in files:
        click.echo(f"Processing: {file}")

        experiment_config = __load_yaml(file)

        init_tasks = load_tasks('init', experiment_config, file)
        final_tasks = load_tasks('final', experiment_config, file)
        before_tasks = load_tasks('before', experiment_config, file)
        after_tasks = load_tasks('after', experiment_config, file)
        tasks = [x for t in experiment_config.get('tasks', []) for x in __transform_task(t)]

        experiment_tasks = [*before_tasks, *tasks, *after_tasks]

        try:
            relative = file.relative_to(Path('experiments'))
        except ValueError:
            # If the file is not inside 'experiments', handle gracefully
            relative = file

        output_dir = Path('data') / relative.parent / relative.stem

        # Render template
        template = JINJA2_ENV.get_template(EXPERIMENT_TEMPLATE)
        yaml_experiment_tasks = yaml.dump(experiment_tasks, width=float("inf"))
        yaml_experiment_tasks = indent_yaml(yaml_experiment_tasks)

        kwargs = {
            'experiment_tasks': yaml_experiment_tasks,
            'output_dir': output_dir.absolute(),
            'base_dir': Path('.').absolute(),
        }
        if init_tasks:
            yaml_init_tasks = yaml.dump(init_tasks, width=float("inf"))
            yaml_init_tasks = indent_yaml(yaml_init_tasks)
            kwargs['init_tasks'] = yaml_init_tasks
        if final_tasks:
            yaml_final_tasks = yaml.dump(final_tasks, width=float("inf"))
            yaml_final_tasks = indent_yaml(yaml_final_tasks)
            kwargs['final_tasks'] = yaml_final_tasks
        rendered = template.render(
            **kwargs
        )

        new_file = file.parent / f'{file.stem}.rendered.yml'

        with open(new_file, 'w') as f:
            f.write(rendered)

        click.echo(f"Rendered file created: {new_file}")

        # Run ansible or other processor
        run_ansible(new_file)
        click.echo(f"Finished processing: {file}\n")

        if not prevent_clean:
            new_file.unlink()



if __name__ == '__main__':
    main()

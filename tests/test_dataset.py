import pytest
import tempfile
import os
import pandas as pd

from prompt_optimizer.dataset import DatasetLoader
from prompt_optimizer.models import TaskBundle


def test_valid_csv_loading():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("system_prompt,prompt,input,expected_output,group_id,case_id\n")
        f.write('"Sys","User {input}","In1","Out1","g1","c1"\n')
        f.write('"Sys","User {input}","In2","Out2","g1","c2"\n')
        path = f.name

    try:
        loader = DatasetLoader(path)
        bundle = loader.load()
        assert isinstance(bundle, TaskBundle)
        assert bundle.system_prompt == "Sys"
        assert len(bundle.groups) == 1
        assert bundle.groups[0].group_id == "g1"
        assert len(bundle.groups[0].test_cases) == 2
    finally:
        os.remove(path)

def test_missing_required_columns():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("prompt,input,expected_output\n")
        f.write('"User {input}","In1","Out1"\n')
        path = f.name

    try:
        loader = DatasetLoader(path)
        with pytest.raises(ValueError, match="Fehlende Pflichtspalten"):
            loader.load()
    finally:
        os.remove(path)

def test_empty_input_rejected():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("system_prompt,prompt,input,expected_output\n")
        f.write('"Sys","User {input}"," ","Out1"\n')
        path = f.name

    try:
        loader = DatasetLoader(path)
        with pytest.raises(ValueError, match="Leerer Input"):
            loader.load()
    finally:
        os.remove(path)

def test_multiple_system_prompts_rejected():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("system_prompt,prompt,input,expected_output\n")
        f.write('"Sys1","User {input}","In1","Out1"\n')
        f.write('"Sys2","User {input}","In2","Out2"\n')
        path = f.name

    try:
        loader = DatasetLoader(path)
        with pytest.raises(ValueError, match="nur einen globalen system_prompt"):
            loader.load()
    finally:
        os.remove(path)

def test_generate_missing_ids():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("system_prompt,prompt,input,expected_output\n")
        f.write('"Sys","User1","In1","Out1"\n')
        f.write('"Sys","User2","In2","Out2"\n')
        path = f.name

    try:
        loader = DatasetLoader(path)
        bundle = loader.load()
        assert len(bundle.groups) == 2
        assert bundle.groups[0].group_id.startswith("group_")
        assert bundle.groups[0].test_cases[0].case_id.startswith("case_")
    finally:
        os.remove(path)

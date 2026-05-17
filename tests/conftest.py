import pytest
import textwrap

@pytest.fixture
def basic_dimacs_net(tmp_path):
    """Generates a small temporary single-commodity DIMACS .min file for quick validation."""
    def _create_net(nodes=5, arcs=10):
        input_path = tmp_path / f"graph_{nodes}_{arcs}.min"
        content = textwrap.dedent("""\
            c Small test network
            p min 5 10
            n 1 10
            n 5 -10
            a 1 2 0 10 11
            a 1 4 0 16 17
            a 2 4 0 10 10
            a 2 3 0 10 12
            a 3 5 0 10 11
            a 3 2 0 20 23
            a 3 4 0 17 15
            a 4 3 0 10 11
            a 4 1 0 10 10
            a 4 2 0 19 22 
        """)
        input_path.write_text(content)
        return str(input_path)
    return _create_net
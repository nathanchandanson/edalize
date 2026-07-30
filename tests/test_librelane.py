from .edalize_common import make_edalize_test
import os


def test_librelane(make_edalize_test):
    tool_options = {
        'flow'      : 'Chip',
        'remove_steps' : ['Verilator.Lint', 'Checker.LintTimingConstructs', 'Checker.LintErrors', 'Checker.LintWarnings'],
        'disable_variables' : ['ERROR_ON_SYNTH_CHECKS', 'PDN_ENABLE_PINS'],
        'enable_variables' : ['USE_SLANG'],
        'additional_variables' : ['PDN_CORE_RING_VWIDTH: 15', 'PDN_CORE_RING_HWIDTH: 15'],
        'clock_port': 'clk_i',
        'clock_period': 20,
        'die_area': [0,0,1000.5,1000.2],
        'core_area': [100,100,900.8,900.1],
        'pad_north': ["clk_i", "rst_ni", "gpio_i1"],
        'pad_south': ["gpio_i2", "gpio_i3", "gpio_i4"],
        'pad_east': ["gpio_i5", "gpio_i6", "gpio_i7"]
    }
    paramtypes = ["vlogdefine"]

    tf = make_edalize_test(
        "librelane", tool_options=tool_options, param_types=paramtypes
    )

    tf.backend.configure()
    tf.backend.build()
    tf.compare_files(["librelane_config.yaml", "Makefile"])

# Copyright edalize contributors
# Licensed under the 2-Clause BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-2-Clause

import logging
import os.path
from edalize.edatool import Edatool

logger = logging.getLogger(__name__)

class Librelane(Edatool):

    argtypes = ["vlogdefine", "vlogparam"]

    @classmethod
    def get_doc(cls, api_ver):
        if api_ver == 0:
            return {'description' : "Open source flow for ASIC synthesis, placement and routing",
                    'members': [
                        {
                            "name": "pdk",
                            "type": "String",
                            "desc": "The name of the PDK to use.",
                        },
                        {
                            "name": "pdk_root",
                            "type": "String",
                            "desc": "The path to the folder containing the PDK.",
                        },
                        {
                            "name": "flow",
                            "type": "String",
                            "desc": "The librelane flow to use (Classic, Chip,...).",
                        },
                        {
                            "name": "clock_port",
                            "type": "String",
                            "desc": "The clock port name.",
                        },
                        {
                            "name": "clock_net",
                            "type": "String",
                            "desc": "The clock net name.",
                        },
                        {
                            "name": "clock_period",
                            "type": "String",
                            "desc": "The clock period in ns.",
                        },
                    ],
                    'lists' : [
                        {
                            "name": "remove_steps",
                            "type": "String",
                            "desc": "The list of all the steps to remove.",
                        },
                        {
                            "name": "disable_variables",
                            "type": "String",
                            "desc": "The list of all the librelane config variables that will be set to False.",
                        },
                        {
                            "name": "enable_variables",
                            "type": "String",
                            "desc": "The list of all the librelane config variables that will be set to True.",
                        },
                        {
                            "name": "additional_variables",
                            "type": "String",
                            "desc": "The list of all the librelane config variables with their values. Ex.: 'PDN_CORE_RING_VWIDTH: 15'",
                        },
                        {
                            "name": "core_area",
                            "type": "String",
                            "desc": "The core area as a list of 4 decimal numbers.",
                        },
                        {
                            "name": "die_area",
                            "type": "String",
                            "desc": "The die area as a list of 4 decimal numbers.",
                        },
                        {
                            "name": "pad_north",
                            "type": "String",
                            "desc": "The north pads as a list.",
                        },
                        {
                            "name": "pad_south",
                            "type": "String",
                            "desc": "The south pads as a list.",
                        },
                        {
                            "name": "pad_west",
                            "type": "String",
                            "desc": "The west pads as a list.",
                        },
                        {
                            "name": "pad_east",
                            "type": "String",
                            "desc": "The east pads as a list.",
                        },
                    ]}

    def configure_main(self):
        pdk                     = self.tool_options.get('pdk')
        pdk_root                = self.tool_options.get('pdk_root')
        flow                    = self.tool_options.get('flow')
        remove_steps            = self.tool_options.get('remove_steps')
        disable_variables       = self.tool_options.get('disable_variables')
        enable_variables        = self.tool_options.get('enable_variables')
        additional_variables    = self.tool_options.get('additional_variables')

        design_name             = self.toplevel
        clock_port              = self.tool_options.get('clock_port')
        clock_net               = self.tool_options.get('clock_net')
        clock_period            = self.tool_options.get('clock_period')

        verilog_files           = []
        verilog_include_dirs    = []
        verilog_defines         = self.vlogdefine

        core_area               = self.tool_options.get('core_area')
        die_area                = self.tool_options.get('die_area')
        pad_north               = self.tool_options.get('pad_north')
        pad_south               = self.tool_options.get('pad_south')
        pad_west                = self.tool_options.get('pad_west')
        pad_east                = self.tool_options.get('pad_east')

        # Additional files
        vlt_files = []
        additional_config_files = []
        tcl_pdn = ""
        macro_placement = ""
        pin_order = ""

        (src_files, verilog_include_dirs) = self._get_fileset_files()
        for f in src_files:
            if f.file_type == 'verilogSource' or f.file_type == 'systemVerilogSource':
                verilog_files.append(f.name)
                # if f.file_type == 'systemVerilogSource':
                #     use_system_verilog = True
            if f.file_type == 'librelaneConfig':
                additional_config_files.append(f.name)
            elif f.file_type == 'pdn':
                tcl_pdn = f.name
            elif f.file_type == 'macroPlacement':
                macro_placement = f.name
            elif f.file_type == 'pinOrder':
                pin_order = f.name
            elif f.file_type == 'vlt':
                vlt_files.append(f.name)

        template_vars = {
            'pdk'                     : pdk,
            'pdk_root'                : pdk_root,
            'flow'                    : flow,
            'remove_steps'            : remove_steps,
            'disable_variables'       : disable_variables,
            'enable_variables'        : enable_variables,
            'additional_variables'    : additional_variables,

            'design_name'             : design_name,
            'clock_port'              : clock_port,
            'clock_net'               : clock_net,
            'clock_period'            : clock_period,

            'verilog_files'           : verilog_files,
            'verilog_include_dirs'    : verilog_include_dirs,
            'verilog_defines'         : verilog_defines,

            'core_area'               : core_area,
            'die_area'                : die_area,
            'pad_north'               : pad_north,
            'pad_south'               : pad_south,
            'pad_west'                : pad_west,
            'pad_east'                : pad_east,

            'vlt_files'               : vlt_files,
            'additional_config_files' : additional_config_files,
            'tcl_pdn'                 : tcl_pdn,
            'macro_placement'         : macro_placement,
            'pin_order'               : pin_order,
        }

        # Check for mandatory arguments
        if (template_vars['pdk'] == None):
            template_vars['pdk'] = 'ihp-sg13g2'
            logger.warning("No PDK specified, using default (IHP-SG13G2).")
        if (template_vars['pdk_root'] == None):
            template_vars['pdk_root'] = '~/.ciel'
            logger.warning("No PDK_ROOT specified, using default (~/.ciel).")
        if (template_vars['pdk'] == None):
            pdk = pdk if (pdk != None) else 'ihp-sg13g2'
        if (template_vars['design_name'] == None):
            logger.error("Please provide a toplevel.")
        if (template_vars['clock_port'] == None):
            logger.error("Please provide a clock_port.")
        if (template_vars['clock_period'] == None):
            logger.error("Please provide a clock_period.")
        if (template_vars['core_area'] == None):
            logger.error("Please provide a core_area.")
        if (template_vars['die_area'] == None and template_vars['flow'] == "Chip"):
            logger.error("Please provide a die_area for the Chip flow.")
        if (template_vars['flow'] != "Chip" and template_vars['flow'] != "Classic"):
            logger.error("flow must be either Chip or Classic.")

        # Generate the templates
        script_name = 'librelane_config.yaml'
        self.render_template('librelane-config.j2', script_name, template_vars)

        makefile_name = 'Makefile'
        self.render_template('librelane-makefile.j2', makefile_name, template_vars)


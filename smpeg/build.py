#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder()
    for settings, options, env_vars, build_requires, reference in builder.items:
        options['sdl2:shared'] = options['smpeg2:shared']
    builder.run()

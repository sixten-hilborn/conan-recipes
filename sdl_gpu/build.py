#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder()
    # Only build static in CI for now
    builder.items = [build for build in builder.items if build[1]['sdl_gpu:shared'] == False]
    builder.run()

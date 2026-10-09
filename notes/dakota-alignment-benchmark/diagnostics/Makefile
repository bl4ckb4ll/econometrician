ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../../..)
ICK_CC ?= ick
ICK_NUMERIC_INCLUDE ?= $(ROOT)/_ick/ick/include
ICK_LINK_FLAGS ?= -fno-link-libatomic
OUTPUT ?= /tmp/low-precision-jacobian

.PHONY: build
build:
	"$(ICK_CC)" -std=c11 -O2 -Wall -Wextra $(ICK_LINK_FLAGS) $(ICK_SUPPORT_FLAGS) \
	  -I"$(ICK_NUMERIC_INCLUDE)" \
	  "$(ROOT)/notes/dakota-alignment-benchmark/diagnostics/low_precision_jacobian.c" \
	  -o "$(OUTPUT)"

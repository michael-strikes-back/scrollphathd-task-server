
SUBDIRS := $(wildcard */.)

install: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: install $(SUBDIRS)


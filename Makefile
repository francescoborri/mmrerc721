PLOTS_EXT := pdf
AGGREGATION_PERIOD := 7d

COLLECTIONS_TRANSFERS := $(shell ls data/collections/transfers/*.csv)
COLLECTIONS_GAS := $(subst transfers,gas,$(COLLECTIONS_TRANSFERS))
COLLECTIONS := $(basename $(notdir $(COLLECTIONS_GAS)))

GAS_PLOTS := $(foreach plot,mint verify,plots/gas/$(plot).$(PLOTS_EXT))
COLLECTION_PLOTS := $(foreach collection,$(COLLECTIONS),$(foreach plot,mint verify,plots/collections/$(collection)/$(plot).$(PLOTS_EXT)))

all : $(GAS_PLOTS) $(COLLECTION_PLOTS)

data/gas/derived/gas.csv : data/gas/raw/mint.csv data/gas/raw/verify.csv
	python3 scripts/gas/merge_gas.py $^ $@

data/gas/derived/max.csv : data/gas/derived/gas.csv data/gas/raw/max_verify.csv
	python3 scripts/gas/max_gas.py $^ $@

data/gas/derived/extended_gas.csv : data/gas/derived/gas.csv data/gas/derived/max.csv
	python3 scripts/gas/extend_gas.py $^ $@

$(COLLECTIONS_GAS) : data/collections/gas/%.csv : data/gas/derived/extended_gas.csv data/collections/transfers/%.csv
	python3 scripts/collection/collection_gas.py $^ $@ --period $(AGGREGATION_PERIOD)

$(GAS_PLOTS) : plots/gas/%.$(PLOTS_EXT) : data/gas/derived/gas.csv data/gas/derived/max.csv
	python3 scripts/plot/plot_gas.py $^ $@ --plot $(basename $(notdir $@))

clean_gas:
	$(RM) -r data/gas/derived

clean_collection_gas:
	$(RM) -r data/collections/gas

clean_plots:
	$(RM) -r plots

clean: clean_gas clean_collection_gas clean_plots

.PHONY: all clean_gas clean_collection_gas clean_plots clean

.SECONDEXPANSION:

$(COLLECTION_PLOTS) : plots/collections/%.$(PLOTS_EXT) : data/collections/gas/$$(subst /,,$$(dir %)).csv data/gas/derived/gas.csv
	python3 scripts/plot/plot_collection_gas.py $^ $@ --plot $(basename $(notdir $@))


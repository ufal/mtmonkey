ORIG_DATA_DIR=orig_data
DATA_DIR=data

all : $(DATA_DIR)/data.prepared $(DATA_DIR)/annot.prepared

$(DATA_DIR)/data.prepared :
	mkdir -p $(DATA_DIR)
	cp $(ORIG_DATA_DIR)/eHealth-test-* $(DATA_DIR)
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.cs > $(DATA_DIR)/eHealth-test.cs
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.de > $(DATA_DIR)/eHealth-test.de
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.en > $(DATA_DIR)/eHealth-test.en
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.fr > $(DATA_DIR)/eHealth-test.fr
	touch $@

$(DATA_DIR)/annot.prepared :
	./prepare_to_annot.pl cs data/eHealth-test
	./prepare_to_annot.pl de data/eHealth-test
	./prepare_to_annot.pl fr data/eHealth-test
	touch $@

ANNOT_DIR=/net/data/khresmoi/queries_eval
copy :
	cp -n $(DATA_DIR)/eHealth-test.cs.to_annot /net/data/khresmoi/queries_eval/
	cp -n $(DATA_DIR)/eHealth-test.de.to_annot /net/data/khresmoi/queries_eval/
	cp -n $(DATA_DIR)/eHealth-test.fr.to_annot /net/data/khresmoi/queries_eval/

man_eval_stats:
	mkdir -p stats
	./annot_stats.pl cs > stats/eHealth-test.cs.stats
	./annot_stats.pl de > stats/eHealth-test.de.stats
	./annot_stats.pl fr > stats/eHealth-test.fr.stats

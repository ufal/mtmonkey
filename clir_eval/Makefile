ORIG_DATA_DIR=/net/data/khresmoi/IR/
MT_DATA_DIR=/ha/home/mnovak/projects/phd/papers/2013-aiim-clir/bootstrap
DATA_DIR=data

#DATA_TYPE=eHealth-test
DATA_TYPE=mt-test

all : $(DATA_DIR)/$(DATA_TYPE).prepared $(DATA_DIR)/$(DATA_TYPE).annot.prepared

$(DATA_DIR)/mt-test.prepared :
	mkdir -p $(DATA_DIR)
	head -n 50 $(MT_DATA_DIR)/reference.txt > $(DATA_DIR)/mt-test.en
	tail -n 50 $(MT_DATA_DIR)/reference.txt >> $(DATA_DIR)/mt-test.en
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.cs.gz | head -n 50 > $(DATA_DIR)/mt-test.cs
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.cs.gz | tail -n 50 >> $(DATA_DIR)/mt-test.cs
	head -n 50 $(MT_DATA_DIR)/cs/03-P0M0.txt > $(DATA_DIR)/mt-test-b0.cs-en
	tail -n 50 $(MT_DATA_DIR)/cs/03-P0M0.txt >> $(DATA_DIR)/mt-test-b0.cs-en
	head -n 50 $(MT_DATA_DIR)/cs/13-P5M4.txt > $(DATA_DIR)/mt-test-v1.cs-en
	tail -n 50 $(MT_DATA_DIR)/cs/13-P5M4.txt >> $(DATA_DIR)/mt-test-v1.cs-en
	head -n 50 $(MT_DATA_DIR)/cs/98-Google.txt > $(DATA_DIR)/mt-test-gt.cs-en
	tail -n 50 $(MT_DATA_DIR)/cs/98-Google.txt >> $(DATA_DIR)/mt-test-gt.cs-en
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.de.gz | head -n 50 > $(DATA_DIR)/mt-test.de
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.de.gz | tail -n 50 >> $(DATA_DIR)/mt-test.de
	head -n 50 $(MT_DATA_DIR)/de/03-P0M0.txt > $(DATA_DIR)/mt-test-b0.de-en
	tail -n 50 $(MT_DATA_DIR)/de/03-P0M0.txt >> $(DATA_DIR)/mt-test-b0.de-en
	head -n 50 $(MT_DATA_DIR)/de/13-P5M4.txt > $(DATA_DIR)/mt-test-v1.de-en
	tail -n 50 $(MT_DATA_DIR)/de/13-P5M4.txt >> $(DATA_DIR)/mt-test-v1.de-en
	head -n 50 $(MT_DATA_DIR)/de/15-P5M4C2.txt > $(DATA_DIR)/mt-test-v1d.de-en
	tail -n 50 $(MT_DATA_DIR)/de/15-P5M4C2.txt >> $(DATA_DIR)/mt-test-v1d.de-en
	head -n 50 $(MT_DATA_DIR)/de/98-Google.txt > $(DATA_DIR)/mt-test-gt.de-en
	tail -n 50 $(MT_DATA_DIR)/de/98-Google.txt >> $(DATA_DIR)/mt-test-gt.de-en
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.fr.gz | head -n 50 > $(DATA_DIR)/mt-test.fr
	zcat /net/data/khresmoi/khresmoi/khresmoi-query-test.fr.gz | tail -n 50 >> $(DATA_DIR)/mt-test.fr
	head -n 50 $(MT_DATA_DIR)/fr/03-P0M0.txt > $(DATA_DIR)/mt-test-b0.fr-en
	tail -n 50 $(MT_DATA_DIR)/fr/03-P0M0.txt >> $(DATA_DIR)/mt-test-b0.fr-en
	head -n 50 $(MT_DATA_DIR)/fr/13-P5M4.txt > $(DATA_DIR)/mt-test-v1.fr-en
	tail -n 50 $(MT_DATA_DIR)/fr/13-P5M4.txt >> $(DATA_DIR)/mt-test-v1.fr-en
	head -n 50 $(MT_DATA_DIR)/fr/98-Google.txt > $(DATA_DIR)/mt-test-gt.fr-en
	tail -n 50 $(MT_DATA_DIR)/fr/98-Google.txt >> $(DATA_DIR)/mt-test-gt.fr-en
	touch $@

$(DATA_DIR)/eHealth-test.prepared :
	mkdir -p $(DATA_DIR)
	cp $(ORIG_DATA_DIR)/eHealth-test-* $(DATA_DIR)
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.cs > $(DATA_DIR)/eHealth-test.cs
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.de > $(DATA_DIR)/eHealth-test.de
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.en > $(DATA_DIR)/eHealth-test.en
	tail -n +6 $(ORIG_DATA_DIR)/eHealth-all.fr > $(DATA_DIR)/eHealth-test.fr
	touch $@

$(DATA_DIR)/$(DATA_TYPE).annot.prepared :
	./prepare_to_annot.pl cs data/$(DATA_TYPE)
	./prepare_to_annot.pl de data/$(DATA_TYPE)
	./prepare_to_annot.pl fr data/$(DATA_TYPE)
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

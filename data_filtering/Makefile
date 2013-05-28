DATA_DIR = data
HESSO_DATA_DIR = $(DATA_DIR)/HES-SO
HON_DATA_DIR = $(DATA_DIR)/HON

############### HES-SO ################################

$(DATA_DIR)/hesso.html :
	wget http://casimir.hesge.ch/khresmoi/dublin/
	mv index.html $@

$(DATA_DIR)/hesso.filelist : $(DATA_DIR)/hesso.html
	cat $< | grep -P "<tr.*href" | perl -pe '$$_ =~ s/^.*href="([^"]+)".*$$/$$1/' > $@

hesso_download : $(DATA_DIR)/hesso.filelist
	for i in `cat $<`; do \
		wget $$i; \
		echo mv `echo $$i | sed 's/.*\///'` $(HESSO_DATA_DIR); \
	done

################ HON ###################################

hon_download : $(HON_DATA_DIR)/all.docs.gz
$(HON_DATA_DIR)/all.docs :
	curl 'http://khresmoi:KhresmoiForEurope2012@khresmoi.honservices.org:5984/khresmoi_docs/_all_docs?include_docs=true' > $@

#hon_prepare_to_split: $(HON_DATA_DIR)/all.docs.to_split.gz
#$(HON_DATA_DIR)/all.docs.to_split.gz : $(HON_DATA_DIR)/all.docs.gz
#	zcat $< | sed '1d;$$d;s/,\r$$//' | gzip -c > $@

hon_unique: $(HON_DATA_DIR)/all.docs.unique.gz
$(HON_DATA_DIR)/all.docs.unique.gz : $(HON_DATA_DIR)/all.docs.gz
	qsubmit --jobname="hon_unique" --logdir='log' --sync \
		"zcat $< | sed '1d;$$d;s/,\r$$//' | scripts/remove_duplicates.pl | gzip -c > $@"

hon_split: $(HON_DATA_DIR)/all.docs.split.list
$(HON_DATA_DIR)/all.docs.split.list : $(HON_DATA_DIR)/all.docs.unique.gz
	mkdir -p $(HON_DATA_DIR)/all.docs.split
	qsubmit --jobname="hon_split" --sync 'zcat $< | scripts/gzip_split.pl -l 100000 $(HON_DATA_DIR)/all.docs.split/part_'
	find $(HON_DATA_DIR)/all.docs.split -name 'part_*' | sort > $@

hon_filter: $(HON_DATA_DIR)/all.docs.split.filtered.list
$(HON_DATA_DIR)/all.docs.split.filtered.list : $(HON_DATA_DIR)/all.docs.split.list
	mkdir -p $(HON_DATA_DIR)/all.docs.split.filtered
	for i in `cat $<`; do \
		echo $$i; \
		filename=`echo $$i | tail -c 12`; \
		qsubmit --jobname="hon_filter_$$filename" --logdir='log' \
			"zcat $$i | scripts/extract_from_HON.pl | gzip -c > $(HON_DATA_DIR)/all.docs.split.filtered/$$filename"; \
		sleep 2; \
	done
	while qstat -r -j "hon_filter_"'*' > /dev/null 2>&1; do sleep 2 ; done
	find $(HON_DATA_DIR)/all.docs.split.filtered -name 'part_*' | sort > $@

hon_add_info: $(HON_DATA_DIR)/all.docs.split.info.list
$(HON_DATA_DIR)/all.docs.split.info.list : $(HON_DATA_DIR)/all.docs.split.filtered.list
	mkdir -p $(HON_DATA_DIR)/all.docs.split.info
	for i in `cat $<`; do \
		echo $$i; \
		filename=`echo $$i | tail -c 12`; \
		qsubmit --jobname="hon_info_$$filename" --logdir='log' \
			"zcat $$i | yali-identifier -e -f single -c yali.classes-all.5 > $(HON_DATA_DIR)/all.docs.split.info/$$filename.yali_ids; \
			zcat $$i | scripts/add_info.pl --yali-ids $(HON_DATA_DIR)/all.docs.split.info/$$filename.yali_ids | gzip -c > $(HON_DATA_DIR)/all.docs.split.info/$$filename;\
			rm $(HON_DATA_DIR)/all.docs.split.info/$$filename.yali_ids"; \
		sleep 2; \
	done
	while qstat -r -j "hon_info_"'*' > /dev/null 2>&1; do sleep 2 ; done
	find $(HON_DATA_DIR)/all.docs.split.info -name 'part_*' | sort > $@

LANGUAGE=en

hon_sent_lang : $(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE).list 
$(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE).list : $(HON_DATA_DIR)/all.docs.split.info.list
	mkdir -p $(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE)
	for i in `cat $<`; do \
		filename=`echo $$i | tail -c 12`; \
		qsubmit --jobname="hon_sent_lang-$(LANGUAGE)_$$filename" --logdir='log' \
			"zcat $$i | scripts/print_text.pl -l $(LANGUAGE) | \
			sed 's/$$/\n/' | ../worker/src/perl-scripts/split-sentences.pl -l $(LANGUAGE) | sed '/^<P>$$/d' | \
			gzip -c > $(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE)/$$filename"; \
		sleep 2; \
	done
	while qstat -r -j "hon_sent_lang-$(LANGUAGE)_"'*' > /dev/null 2>&1; do sleep 2 ; done
	find $(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE) -name 'part_*' | sort > $@

hon_merge: /net/data/khresmoi/hon-2013-05/hon.lm.$(LANGUAGE).gz
/net/data/khresmoi/hon-2013-05/hon.lm.$(LANGUAGE).gz : $(HON_DATA_DIR)/all.docs.split.sent_lang.$(LANGUAGE).list
	mkdir -p /net/data/khresmoi/hon-2013-05
	qsubmit --jobname="hon_merge_$(LANGUAGE)" --logdir='log' --sync \
		"cat $< | xargs --verbose -I{} zcat {} | gzip -c > $@"

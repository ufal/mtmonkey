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

hon_download : $(HON_DATA_DIR)/all.docs
$(HON_DATA_DIR)/all.docs :
	curl 'http://khresmoi:KhresmoiForEurope2012@khresmoi.honservices.org:5984/khresmoi_docs/_all_docs?include_docs=true' > $@
	sed -i '1d;$$d;s/\r//;s/,$$//' $@

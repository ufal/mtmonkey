'''
Created on 24 Mar 2012
@author: Lefteris Avramidis
'''
import subprocess
import codecs
import os
import Queue
import threading
import logging as logger

class Preprocessor(object):
    """
    """
    def __init__(self, lang):
        self.lang = lang
    
    def add_features_src(self, simplesentence, parallelsentence = None):
        src_lang = parallelsentence.get_attribute("langsrc") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.lang:
            simplesentence.string = self.process_string(simplesentence.string)  
        return simplesentence
    
    def add_features_tgt(self, simplesentence, parallelsentence = None):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            simplesentence.string = self.process_string(simplesentence.string)  
        return simplesentence
    
    
    def process_string(self, string):
        raise NotImplementedError
    
    
class CommandlinePreprocessor(Preprocessor):
    
    def _enqueue_output(self, stdout, queue):
        out = 0
        for line in iter(stdout.readline, ''):
            print "thread received response: ", line
            queue.put(line)
    
    def __init__(self, path, lang, params = {}, command_template = ""):
        self.lang = lang
        params["lang"] = lang
        params["path"] = path
        self.command = command_template.format(**params)
        command_items = self.command.split(' ')
        self.output = []
        self.running = True
        
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=1, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        )
        

    def process_string(self, string):

        string = string.encode('utf-8')
        #write to the stdin pipe followed by some space bytes in order to flush
        self.process.stdin.write('{0}{1}\n'.format(string, ' '*10240))
        #self.process.stdin.write(string.strip())
        self.process.stdin.flush()   
        self.process.stdout.flush()
        
        output = self.process.stdout.readline().strip()
        
        #some preprocessors occasionally return an empty string. In that case read once more
        if output == "" and len(string) > 1:
            output = self.process.stdout.readline().strip()
        

	output = output.decode('utf-8')
        return output
    
    def close(self):
        self.running = False
        try:
            self.process.stdin.close()
            self.process.terminate()
        except:
            pass
    
    def __del__(self):
        self.close()
    
    def _get_temporary_file(self, strings):
        import tempfile
                
        f, filename = tempfile.mkstemp(text=True)
        os.close(f)
        print filename
        f = open(filename, 'w')
        for string in strings:
            f.write(string)
            f.write('\n')
        f.close()
        return filename
    
    def _get_tool_output(self, strings):
        tmpfilename = self._get_temporary_file(strings)
        tmpfile = open(tmpfilename, 'r')
        commanditems = self.command.split(' ')
        output = subprocess.check_output(commanditems, stdin=tmpfile).split('\n')
        tmpfile.close()
        #os.remove(tmpfile)
        return output

class Normalizer(CommandlinePreprocessor):
    def __init__(self, lang):
	directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'normalize-punctuation.perl')
        command_template = "perl {path} -b -l {lang}"
        super(Normalizer, self).__init__(path, lang, {}, command_template)
        
class Tokenizer(CommandlinePreprocessor):
    def __init__(self, lang):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory,  'tokenizer.perl')
        #TODO: protected parameters causes errors
        #protected = os.path.join(directory, "basic-protected-patterns")
        #logger.warning("Protected patterns loaded from {}".format(protected))
        #command_template = "".join(["perl {path} -p -b -l {lang}", " -protected {}".format(protected)])
        command_template = "perl {path} -p -b -l {lang}"
        super(Tokenizer, self).__init__(path, lang, {}, command_template)

class Detokenizer(CommandlinePreprocessor):
    def __init__(self, lang):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'detokenizer.perl')
        command_template = "perl {path} -l {lang}"
        super(Detokenizer, self).__init__(path, lang, {}, command_template)

class Truecaser(CommandlinePreprocessor):
    def __init__(self, lang, model):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'truecase.perl')
        command_template = "perl {path} -model {model}"
        super(Truecaser, self).__init__(path, lang, {"model": model}, command_template)

class Detruecaser(CommandlinePreprocessor):
    def __init__(self, lang):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'detruecase.perl')
        command_template = "perl {path} -b"
        super(Detruecaser, self).__init__(path, lang, {}, command_template)

class CompoundSplitter(CommandlinePreprocessor):
    def __init__(self, lang, model):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'compound-splitter.perl')
        command_template = "perl {path} -model {model}"
        super(CompoundSplitter, self).__init__(path, lang, {"model": model}, command_template)   


if __name__ == '__main__':
    import sys
    tokenizer = Tokenizer("en")
    string = sys.argv[1]
    print tokenizer.process_string(string)
    



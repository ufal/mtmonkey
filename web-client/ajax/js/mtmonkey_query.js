var origText = "";

/* This calls query.php to translate the input text. */
function translate() {
    $("#cannot").fadeOut();
    origText = $('#src').val();
    if (!origText || 0 == origText.length)
        return;
    srcLang = $('input[name=radio-src]:checked').val();
    destLang = $('input[name=radio-dest]:checked').val();
    if (srcLang == destLang) {
        $("#cannot").fadeIn();
        return;
    }
    $('.working').fadeIn();
    var query = { "action":"translate",
            "text": origText,
            "sourceLang":srcLang,
            "targetLang":destLang,
            "alignmentInfo": "true" };
    $('#q').text(JSON.stringify(query, undefined, 2));
    $.post("query.php",
            query,
            function(data) { show(data); },
            "json");
}

/* This processes the request result */
function show(data) {
    $('.working').fadeOut();
    try {
        if (data['errorCode'] != 0){
            $("#dest").val('Error ' + data['errorCode'] + ': ' + data['errorMessage']);
        }
        else {
            var sentences = data['translation'][0]['translated'];
            // Total translation
            var totalTranslation = "";
            for (var i=0; i<sentences.length; i++)
                totalTranslation += sentences[i]['text'] + " ";
            $("#dest").val(totalTranslation);
            // Each sentences
            $("#align").empty();
            $("#align").append('<h1>Phrase alignment information (mouse hover)</h1>');
            sentences.forEach(showSentenceAlignment);
            // Hovers
            setupHovers();

            $("#align").fadeIn('slow');
        }
        $('#r').text(JSON.stringify(data, undefined, 2));
    }
    catch(exc){
        alert(exc);
        for(key in data){alert(key);}
    }
}

function showSentenceAlignment(sen, idx) {

    // computing zipped alignment
    align = sen['alignment-raw'];
    src_words = sen['src-tokenized'].split(' ');
    tgt_words = sen['tgt-tokenized'].split(' ');
    zip = [];
    for (var i=0; i< align.length; i++){
        a = align[i];
        zip.push([tgt_words.slice(a['tgt-start'], a['tgt-end'] + 1).join(' '), 
                src_words.slice(a['src-start'], a['src-end'] + 1).join(' ')]);
    }

    // displaying the zipped alignment
    var e = $('<div class="sentence" />');
    for (var j=1; j>=0; j--) {
        var x = $('<div class="line" />');
        for (var i=0; i<zip.length; i++) {
            var token = zip[i][j];
            x.append('<span class="token" tokenorder="' + (i + 10000*idx) + '">' +
                        token + '</span>');
        }
        e.append(x);
    }
    $("#align").append(e);
}

function doneTyping() {
    translate();
}

function setupHovers() {
    $("span.token").hover(
        function() {
            var x = $(this);
            var tokenOrder = x.attr('tokenorder');
            $('[tokenorder = ' + tokenOrder + ']').addClass("hover");
        },
        function() {
            var x = $(this);
            var tokenOrder = x.attr('tokenorder');
            $('[tokenorder = ' + tokenOrder + ']').removeClass("hover");
        }
    );
}

/* Shows only compatible language pairs for a source language */
function langSetup() {
    
    $('#dest').val('');
    $('#align').fadeOut();

    $('input[name="radio-dest"]').each(function(){
        $(this).hide();
        $('label[for="' + $(this).attr('id') + '"]').hide();
    });

    curDestLang = $('input[name=radio-dest]:checked').val();
    compatible = $('input[name="radio-src"]:checked').data('compatible');
    if ($.inArray(curDestLang, compatible) < 0){
        $('#radio-dest-' + curDestLang).attr('checked', '');
        curDestLang = null;
    }
    for (var i = 0; i < compatible.length; ++i){
        if (curDestLang == null){
            $('#radio-dest-' + compatible[i]).attr('checked', 'checked');
            curDestLang = compatible[i];
        }
        $('#radio-dest-' + compatible[i]).fadeIn();
        $('label[for="radio-dest-' + compatible[i] + '"]').fadeIn();
    }
}

/* Change the `radioX' numbers here to adjust for the number of language pairs. */
function design() {
    
    $('#src').focus();
    $('input[name="radio-src"]').click(function(){ langSetup(); doneTyping(); });
    $('input[name="radio-dest"]').click(function(){ doneTyping(); });
    $('#go').mouseup(function() {  doneTyping();  });
    $('#detail-show').click(function() {
        $('#detail').fadeToggle(380);
    });
    /**/
}

/* This is run after the page is built */
$(document).ready(function() {
    design();
});

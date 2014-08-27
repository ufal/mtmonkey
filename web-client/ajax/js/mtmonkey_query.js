var origText = "";

function translate() {
    $("#cannot").fadeOut();
    origText = $('#src').val();
    if (!origText || 0 == origText.length)
        return;
    srcLang = $('input[name=radio-src]:checked').attr('l');
    destLang = $('input[name=radio-dest]:checked').attr('l');
    if ((srcLang != "en" && destLang != "en") || (srcLang == destLang)) {
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
    catch(exc){ alert(exc); for(key in data){alert(key);} }
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

var typingTimer;
var doneTypingInterval = 900;

function prep() {
    prep_timer();    
}

function prep_timer() {
/* TIMER!!!
    $('#src').keyup(function() {
        clearTimeout(typingTimer);
        if ($('#src').val) {
            typingTimer = setTimeout(doneTyping, doneTypingInterval);
        }
    });
*/
}

function doneTyping() {
    clearTimeout(typingTimer);
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

function langSetup(isFromEnglish) {
    
    clearTimeout(typingTimer);
    /*  $('#src').val(''); */
    $('#dest').val('');
    $('#align').fadeOut();
    
    if (isFromEnglish) {
        $('#radio5').hide(); $('label[for="radio5"]').hide();
        for (var i=6; i<=8; i++) {
            $("#radio"+i).fadeIn(); $('label[for="radio' + i + '"]').fadeIn();
        }
    } 
    else {
        for (var i=6; i<=8; i++) {
            $("#radio"+i).hide(); $('label[for="radio' + i + '"]').hide();
        }
        $('#radio5').fadeIn(); $('label[for="radio5"]').fadeIn();
    }
}

function design() {
    
    $('#src').focus();
    $('#radio6').click(function() {  doneTyping();  });
    $('#radio7').click(function() {  doneTyping();  });
    $('#radio8').click(function() {  doneTyping();  });
    $('#go').mouseup(function() { console.log('go');  doneTyping(); });
    $('#detail-show').click(function() {
        $('#detail').fadeToggle(380);
    });
    /**/
    $('#radio1').click(function() { $('#radio7').attr('checked','checked'); langSetup(true); doneTyping(); });
    $('#radio2').click(function() { $('#radio5').attr('checked','checked'); langSetup(false); doneTyping(); });
    $('#radio3').click(function() { $('#radio5').attr('checked','checked'); langSetup(false); doneTyping(); });
    $('#radio4').click(function() { $('#radio5').attr('checked','checked'); langSetup(false); doneTyping(); });
}

/* This is run after the page is built */
$(document).ready(function() {
    prep();
    design();
});

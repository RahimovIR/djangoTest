/**
 * Created by ilyas on 23.05.14.
 */

var path = '';
var headerKeys = [];
var fieldType = {};
var verbos_name = {};
var editField = {};
function writeLog(errorStr) {
    $('#errorLog').append(errorStr);
    $('#errorLog').append('</br>');
}
$.ajaxSetup({
    dataType: "json",
    processData:  false,
    async: false,
    contentType: "application/json",
    error: function(jqXHR, exception) {
        var errorHead = 'json error: ';
        if (jqXHR.status === 0) {
            writeLog(errorHead + 'Not connect. Verify Network.');
        } else if (jqXHR.status == 400) {
            writeLog(errorHead + 'Bad Requested: ' + jqXHR.responseText);
        } else if (jqXHR.status == 404) {
            writeLog(errorHead + 'Requested page not found. [404]');
        } else if (jqXHR.status == 500) {
            writeLog(errorHead + 'Internal Server Error [500]: ' + jqXHR.statusText);
        } else if (jqXHR.status == 501) {
            writeLog(errorHead + 'Internal Server Error [501]: ' + jqXHR.statusText);
        } else if (exception === 'parsererror') {
            writeLog(errorHead + 'Requested JSON parse failed.');
        } else if (exception === 'timeout') {
            writeLog(errorHead + 'Time out error.');
        } else if (exception === 'abort') {
            writeLog(errorHead + 'Ajax request aborted.');
        } else {
            writeLog(errorHead + 'Uncaught Error: ' + jqXHR.responseText);
        }
    }
});

$(document).ready(function(){

    $("a.link").click(function(){
        path = $(this).attr("href") + '/';
        headerKeys = [];
        fieldType = {};
        verbos_name = {};
        editField = {};
        updateData();
        return false;
    });
});

function updateData(){
    var table = $('<table border="1">');

    genHeader(table);

    $.getJSON('api/tables' + path, {}, function(json){
        genTable(json, table);
        $("#table").html(table);
    });
}

// Generate tables

function genHeader(table){
    function _genHeader(table){
        var tr = $('<tr>');
        tr.append($('<td>').append('id'));

        for (i=0; i < headerKeys.length; i++){
            tr.append($('<td>').append(verbos_name[headerKeys[i]]));
        }
        tr.append($('<td>').append('action'));
        table.append(tr);
    }

    if ( headerKeys.length == 0){
        $.getJSON('api/tables' + path + 'schema/', {},function(json){
                $.each(json.fields.field_order, function(index, obj){
                    headerKeys[index] = obj;
                    fieldType[obj] = json.fields[obj].type;
                    verbos_name[obj] = json.fields.fields_verbos_name[obj];
                });
                _genHeader(table);
            });
    }else{
        _genHeader(table);
    }
}

function genTable(json, table){
    $.each(json.objects, function(index, obj){
        var tr = $('<tr>');

        tr.append($('<td>').append(obj['id']));
        for (i=0; i < headerKeys.length; i++){
            var td = $('<td id=' + headerKeys[i] + '.' + fieldType[headerKeys[i]] + '>').click(clickTd);
            if (fieldType[headerKeys[i]] == 'datetime'){
                td.pickmeup(
                    {format:'Y-m-d', change: function(val){
                        $('#editField').val(val);
                        $(this).pickmeup('hide');
                        updateRow();
                    }}
                );
            }
            tr.append(td.append( obj[headerKeys[i]] ));
        }
        var delbutton = $('<input type="button" value="del" id="delButton'+ obj['id'] +'"/>');
        delbutton.click(function(){
            id = $(this)[0].id.split('delButton')[1];
//            console.log($(this)[0].id.split('delButton')[1]);
            deleteJson(id);
        });
        td = $('<td>');
        td.append(delbutton);
        tr.append(td);
        table.append(tr);
    });

    var tr = $('<tr>');
    tr.append($('<td>'));
    for (i=0; i < headerKeys.length; i++){
        if (fieldType[headerKeys[i]] == 'datetime'){
            var inputField = $('<input type="datetime"  id=' + headerKeys[i] + '>');
            inputField.pickmeup({format:'Y-m-d', change: function(val){
                inputField.val(val).pickmeup('hide');
            }});
            var td =  $('<td>').append(inputField);
        }else{
            var td =  $('<td>').append($('<input type="text" id=' + headerKeys[i] + ' name=' + headerKeys[i] + '>'));
        }
        tr.append(td);
    }
    var addbutton = $('<input type="button" value="add" id="addButton"/>');
    addbutton.click(function(){
        addNewRow();
    });
    td = $('<td>');
    td.append(addbutton);
    tr.append(td);
    table.append(tr);
}

function clickTd(){
    if ($(this)[0].firstChild.nodeType == 3) {
        var tr = $(this).first().parent();
        editField = {};
        editField['editIndex'] = $(this).index();

        $.each(tr.children(), function(index, obj){
            editField[index] = obj.innerHTML;
        });
        var value = $(this)[0].innerHTML;
        editField['value'] = value;
        headerIndex = editField['editIndex'] - 1;
        if (fieldType[headerKeys[headerIndex]] == 'datetime'){
            var inputField = $('<input type="datetime" id="editField" value="' + value + '" ' +
                'onkeyup="handleKeyPress(event)" + onblur="cancelEdit()">');
        }else{
            var inputField = $('<input type="text" id="editField" value="' + value + '" ' +
                'onkeyup="handleKeyPress(event)" + onblur="cancelEdit()">');
        }
        $(this).html(inputField);
        $(this).children().first().focus();
    }
}

function handleKeyPress(event){
    if(event.keyCode === 13){ // enter
        editField[editField['editIndex']] = $('#editField').val();
        updateRow();
    }
    if(event.keyCode === 27){ // esc
        cancelEdit();
    }
}

function validValue(value, type){
    var errorHead = 'valid error: ';
    if(value ==''){
        writeLog(errorHead + 'field empty');
        return false;
    }
    if(type == 'integer'){
        if(parseFloat(value) == parseInt(value, 10) && !isNaN(value)){
            return true;
        }else{
            writeLog(errorHead + value + ' is not integer');
            return false;
        }
    }
    if(type == 'datetime'){
        if( ! /^\d{4}-\d{2}-\d{2}$/.test(value)){
            writeLog(errorHead + value + ' is not date1');
            return false;
        }
        var formats = ['YYYY-MM-DD'];
        if(moment(value, formats).isValid()){
            return true;
        }else{
            writeLog(errorHead + value + ' is not date2');
            return false;
        }
    }
    if(type == 'string'){
        return true;
    }
}

function updateRow(){
    editField[editField['editIndex']] = $('#editField').val();
    var values = {};
    var fieldsValid = true;
    for (i=0; i<headerKeys.length; i++){
        var fname = headerKeys[i];
        var ftype = fieldType[fname];
        var value = editField[i + 1];
        if( ! validValue(value, ftype)){
            fieldsValid = false;
        }
        values[headerKeys[i]] = value;
    }
    values['id'] = editField[0];
    if (fieldsValid){
        $('td').pickmeup('hide');
        postJson(values);
    }
}

function addNewRow(){
    var values = {};
    var errorStr = '';
    var fieldsValid = true;
    for (i=0; i<headerKeys.length; i++){
        var fname = headerKeys[i];
        var ftype = fieldType[fname];
        var value = $("#" + headerKeys[i]).val();
        if( ! validValue(value, ftype)){
            fieldsValid = false;
        }
        values[headerKeys[i]] = value;
    }
    if (fieldsValid){
        postJson(values);
    }
}

function postJson(value){
    var jsonValue = JSON.stringify(value);
    $.ajax({
        type: 'POST',
        url: 'api/tables' + path,
        data: jsonValue,
        success: writeLog('info: send post')
    });
    updateData();
}

function deleteJson(id){
    $.ajax({
        type: 'DELETE',
        url: 'api/tables' + path + id + '/',
        success: writeLog('info: send delete')
    });
    updateData();
}

function cancelEdit(){
    $('td').pickmeup('hide');
    var td = $('#editField').first().parent();
    td.html(editField['value']);
}

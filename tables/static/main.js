/**
 * Created by ilyas on 23.05.14.
 */

var path = '';
var headerKeys = [];
var fieldType = [];
var verbos_name = [];
var editField = {};
$.ajaxSetup({async: false});

$(function(){

    $("a.link").click(function(){
        path = $(this).attr("href") + '/';
        headerKeys = [];
        fieldType = [];
        verbos_name = [];
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
            var td = $('<td>').click(clickTd);
            tr.append(td.append( obj[headerKeys[i]] ));
        }
        var delbutton = $('<input type="button" value="del" id="delButton'+ obj['id'] +'"/>');
        delbutton.click(function(){
            id = $(this)[0].id.split('delButton')[1];
            console.log($(this)[0].id.split('delButton')[1]);
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
            var td =  $('<td>').append($('<input type="text"  id=' + headerKeys[i] + '>'));
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
                'onkeypress="handleKeyPress(event)" + onblur="cancelEdit()">');
            inputField.pickmeup({format:'Y-m-d', change: function(val){
                inputField.val(val).pickmeup('hide');
            }});
        }else{
            var inputField = $('<input type="text" id="editField" value="' + value + '" ' +
                'onkeypress="handleKeyPress(event)" + onblur="cancelEdit()">');
        }
        $(this).html(inputField);
        $(this).children().first().focus();
    }
}

function handleKeyPress(event){
    if(event.keyCode === 13){
        editField[editField['editIndex']] = $('#editField').val();
        updateRow();
    }
}

function updateRow(){
    var values = {};
    for (i=0; i<headerKeys.length; i++){
        values[headerKeys[i]] = editField[i + 1];
    }
    values['id'] = editField[0];
    postJson(values);
}

function addNewRow(){
    var values = {};
    for (i=0; i<headerKeys.length; i++){
        values[headerKeys[i]] = $("#" + headerKeys[i]).val();
    }
    postJson(values);
}

function postJson(value){
    var jsonValue = JSON.stringify(value);
    $.ajax({
        type: 'POST',
        url: 'api/tables' + path,
        data: jsonValue,
        success: console.log('send post'),
        dataType: "application/json",
        processData:  false,
        async: false,
        contentType: "application/json"
    });
    updateData();
}

function deleteJson(id){
    $.ajax({
        type: 'DELETE',
        url: 'api/tables' + path + id,
        success: console.log('send delete'),
        dataType: "application/json",
        processData:  false,
        async: false,
        contentType: "application/json"
    });
    updateData();
}

function cancelEdit(){
    updateData();
}

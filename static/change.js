
function manu_triangle()
{

    let value3_Type_triangle = document.querySelector('#value3_Type_triangle').value
    selected_input = $('#change')[0];

    var angle_opt = document.querySelector('#angle_opt');
    var change = document.querySelector('#change');

    change.style.visibility = "visible";

    angle_opt.style.visibility = "hidden";

    document.getElementById("angle").innerHTML = " ";



    if (value3_Type_triangle === "none")
    {
        $("#change").prop('disabled', true);
        change.style.visibility = "hidden";
    }
    else
    {
        $("#change").prop('disabled', false);
    }


    if (value3_Type_triangle === "angle_L" || value3_Type_triangle === "angle_R")
    {

        selected_input.placeholder = "In Degrees (°)";
    }

    if (value3_Type_triangle === "length_L" || value3_Type_triangle === "length_R")
    {
        angle_opt.style.visibility = "visible";
        if (value3_Type_triangle === "length_L" ) {   document.getElementById("angle").innerHTML = "Left-corner angle: ";    }
        if (value3_Type_triangle === "length_R" ) {   document.getElementById("angle").innerHTML = "Right-corner angle: ";    }

        selected_input.placeholder = "Enter the length";
        // changing min value for side length input
        change.min = document.querySelector("#height").value;
    }


    /* very useful!!
    $("#put_given_id_of_form_to_disable_all_the_inputs :input").prop("disabled", false);
    */
}





document.querySelector('#for_js').onmousemove = function ()
{
   manu_triangle();

}

document.querySelector('#value3_Type_triangle').onchange = function ()
{
   manu_triangle();

}



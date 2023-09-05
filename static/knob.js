$(document) .ready(function() {
    // let tempo = $(".tempo");
    let knob = $(".knob");

    $(function() {
        $(".knob").knob({
            // Customize the knob
            'min': 0,
            'max': 200,
            'height': 140,
            'width': 200,
            'font': 'Roboto',
            'fontWeight': 'bold',
            'inputColor': 'yellow',
            'bgColor': '#706A70',
            'fgColor': 'yellow',
            'thickness': .3,
            'angleArc': 180,
            'angleOffset': -90,
            'lineCap': 'round',

            // Display the Tempo value
            // 'change': function (value) {
            //     tempo.text(Math.round(value));
            // }
        });

        // Display the initial value
        // tempo.text($(".knob").val());
        
        // Check the manual input
        knob.on('input', function() {
            let inputValue = $(this).val(); // Get the current value from the input field
            if (inputValue > 200) { // If the value is greater than 200
                inputValue = 200; // Set the value to 200

            } else if ((inputValue < 0) || isNaN(inputValue)) { // If the value is less than 0 or not a number
                inputValue = 0; // Set the value to 0
            }
             // Update the input value and trigger the change event
            $(this).val(inputValue).trigger('change');
            // tempo.text(Math.round(inputValue)); // Update the BPM display
        });

        // Custom CSS
        $(".knob").css({
            'font-size':'40px',   
            'margin-top':'-70px',
        });
    });

    




    
});
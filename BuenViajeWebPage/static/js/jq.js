/**
 * Created by Carlos on 2/19/2015.
 */
var interval = 200;
window.onload = function () {
    $(".member>.member-show-info").click(function () {
        $(this).next().slideToggle(interval, "linear");
    });
};

function expand() {
    $(".member-extra-info").slideDown(interval + 200, "linear");
    $("#expand_all").css('display', 'None');
    $("#collapse_all").css('display', "");
}
function collapse() {
    $(".member-extra-info").slideUp(interval + 200, "linear");
    $("#collapse_all").css('display', 'None');
    $("#expand_all").css('display', "");
}
function pictures() {
    var aa = document.getElementsByClassName("item");
    for (var i = 0; i < aa.length; i++) {
        aa[i].onclick = function () {
            show_image(this);
        }
    }
}

function show_image(node) {
    var big_div = document.createElement("div");
    big_div.id = "big_div";

    //This creates the shadow effect
    var background_div = document.createElement("div");
    background_div.id = "background_div";
    background_div.onclick = function () {
        $("#big_div").fadeOut("slow", function () {
            var bg_dv = document.getElementById("big_div");
            document.getElementsByTagName("body")[0].removeChild(bg_dv);
        });
    };

    //Here goes the content
    var container_div = document.createElement("div");
    container_div.id = "container_div";
    var the_img_src = node.firstChild.src;
    var the_img_caption = document.createElement("p");
    the_img_caption.innerHTML = node.lastChild.innerHTML;
    var the_img = document.createElement("img");
    the_img.src = the_img_src;
    container_div.appendChild(the_img);
    container_div.appendChild(the_img_caption);

    big_div.appendChild(background_div);
    big_div.appendChild(container_div);

    document.getElementsByTagName("body")[0].appendChild(big_div);

    $("#big_div").fadeIn("slow");
}

function prep_the_pictures(id, info) {
    var image_container = document.getElementById("demo" + id);
    for (var i = 0; i < info[0].length; i++) {
        var divv = document.createElement("div");
        divv.className = "item";
        divv.setAttribute("data-w", info[i][1]);
        divv.setAttribute("data-h", info[i][2]);
        divv.onclick = function () {
            show_image(this);
        };
        var img = document.createElement("img");
        img.src = info[i][0];
        var tag = document.createElement("a");
        tag.innerHTML = info[i][3];
        divv.appendChild(img);
        divv.appendChild(tag);
        image_container.appendChild(divv);
    }
}




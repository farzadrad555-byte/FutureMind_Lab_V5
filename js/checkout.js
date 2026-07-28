
async function submitOrder(){

    console.log("SUBMIT CLICKED");
    console.log("PRODUCT:", window.selectedProduct);

    if(!window.productReady || !window.selectedProduct){
        alert("Please wait, product is loading...");
        return;
    }

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;

    if(!name || !email){
        alert("Please enter your name and email");
        return;
    }

    const orderData = {

        name: name,
        email: email,

        product: window.selectedProduct.name,
        product_id: window.selectedProduct.id,

        amount: window.selectedProduct.price,

        currency: "USD",
        payment_method: "TEST"

    };


    try{

        const response = await fetch("/api/order",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(orderData)

        });


        const data = await response.json();


        if(data.status === "success"){

            localStorage.setItem(
                "order_id",
                data.order_id
            );

            window.location.href =
            "order_success.html";

        }
        else{

            alert("Order failed");

        }

    }

    catch(error){

        console.log(error);

        alert("Connection error");

    }

}


async function submitOrder(){

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();

    if(!name || !email){
        alert("Please enter your name and email.");
        return;
    }

    const order = {
        name: name,
        email: email,
        product: "Hunter-X V44 Professional"
    };

    try {

        const response = await fetch("/api/order",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify(order)
        });

        const result = await response.json();

        if(result.status === "success"){
            window.location.href="/thank-you.html";
        }
        else{
            alert("Order failed. Please try again.");
        }

    } catch(error){

        alert("Connection error. Please try again.");

    }
}

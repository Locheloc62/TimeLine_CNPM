function addToCart(id, name, price){
    fetch('/api/carts',{
        method: 'post',
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res =>res.json()).then(data=>{
        let d = document.getElementsByClassName("class_counter");
        for(let e of d){
            e.innerText = data.total_quantity;
        }
    })
}

function updateCart(productId, obj){
    fetch(`api/cart/${productId}`, {
                method: 'put',
                body: JSON.stringify({
                    "quantity": parseInt(obj.value)
                }),
                headers: {
                    "Content-Type": "application/json"
                }
    }).then(res=>res.json()).then(data=>{

        let d = document.getElementsByClassName("class_counter");
        for(let e of d){
            e.innerText = data.total_quantity;
        }

        let d2 = document.getElementsByClassName("class_amount");
        for(let e of d2){
            e.innerText = data.total_amount.toLocaleString("en");
        }
    })
}

function fetchSalesData(month, type) {
  return fetch('/static/data/products.json')  // Đường dẫn đến file JSON
    .then(res => res.json())
    .then(data => {
      const filtered = data.filter(item => item.month === month);
      const labels = filtered.map(item => item.name);
      const values = type === 'revenue'
        ? filtered.map(item => item.price * item.sold)
        : filtered.map(item => item.sold);

      return { labels, values };
    });
}

function deleteCart(id){
    if(confirm("Bạn có chắc chắn xóa?")===true){
        fetch(`api/cart/${id}`, {
            method: 'delete'
        }).then(res=>res.json()).then(data=>{

            let d = document.getElementsByClassName("class_counter");
            for(let e of d){
                e.innerText = data.total_quantity;
            }

            let d2 = document.getElementsByClassName("class_amount");
            for(let e of d2){
                e.innerText = data.total_amount.toLocaleString("en");
            }

            let e = document.getElementById(`product${id}`);
            e.style.display = "none";
        })
    }
}

function pay(){
    if(confirm("Bạn có chắc chắn thanh toán!")==true){
        fetch("/api/pay",{
            method: "post"
        }).then(res=>res.json()).then(data=>{
            if(data.status===200){
                location.reload();
            }else
                alert("Error!");
        })
    }
}
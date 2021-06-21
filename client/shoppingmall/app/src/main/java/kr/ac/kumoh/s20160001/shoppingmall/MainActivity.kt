package kr.ac.kumoh.s20160001.shoppingmall

import android.content.DialogInterface
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.DefaultItemAnimator
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.recyclerview.widget.StaggeredGridLayoutManager
import kotlinx.android.synthetic.main.activity_main.*


class MainActivity : AppCompatActivity() {
    private lateinit var model: ViewModel
    private val mAdapter = ProductAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val btn2 = findViewById<TextView>(R.id.cat2)
        val btn3 = findViewById<TextView>(R.id.cat3)
        val btn4 = findViewById<TextView>(R.id.cat4)
        val btn5 = findViewById<TextView>(R.id.cat5)
        val btn6 = findViewById<TextView>(R.id.cat6)


        btn2.setOnClickListener {
            var builder = AlertDialog.Builder(this)
            builder.setTitle("죄송합니다.")
            builder.setMessage("죄송합니다. 아직 해당 카테고리 상품이 준비되지 않았습니다.")
            builder.show()
        }
        btn3.setOnClickListener {
            var builder = AlertDialog.Builder(this)
            builder.setTitle("죄송합니다.")
            builder.setMessage("죄송합니다. 아직 해당 카테고리 상품이 준비되지 않았습니다.")
            builder.show()

        }
        btn4.setOnClickListener {
            var builder = AlertDialog.Builder(this)
            builder.setTitle("죄송합니다.")
            builder.setMessage("죄송합니다. 아직 해당 카테고리 상품이 준비되지 않았습니다.")
            builder.show()

        }
        btn5.setOnClickListener {
            var builder = AlertDialog.Builder(this)
            builder.setTitle("죄송합니다.")
            builder.setMessage("죄송합니다. 아직 해당 카테고리 상품이 준비되지 않았습니다.")
            builder.show()

        }
        btn6.setOnClickListener {
            var builder = AlertDialog.Builder(this)
            builder.setTitle("죄송합니다.")
            builder.setMessage("죄송합니다. 아직 해당 카테고리 상품이 준비되지 않았습니다.")
            builder.show()

        }

        product_list.apply {
            layoutManager = StaggeredGridLayoutManager(3,LinearLayoutManager.VERTICAL)
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
            adapter = mAdapter
        }

        model = ViewModelProvider(this,
            ViewModelProvider.AndroidViewModelFactory(application))
            .get(ViewModel::class.java)

        model.list.observe(this, Observer<ArrayList<ViewModel.Product>> {
            mAdapter.notifyDataSetChanged()
        })

        model.getInfo()
    }

    inner class ProductAdapter: RecyclerView.Adapter<ProductAdapter.ViewHolder>() {

        inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
            val txName = itemView.findViewById<TextView>(R.id.text1)
            val txPrice = itemView.findViewById<TextView>(R.id.text2)
            val productImg = itemView.findViewById<ImageView>(R.id.image1)
        }

        override fun getItemCount(): Int {
            return model.getSize()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductAdapter.ViewHolder {
            val view = layoutInflater.inflate(
                R.layout.rankview,
                parent,
                false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ProductAdapter.ViewHolder, position: Int) {
            holder.txName.text = model.getProduct(position).name
            holder.txPrice.text = model.getProduct(position).price
            model.setImg(model.getProduct(position).id,holder.productImg)

            holder.itemView.setOnClickListener(){
                val intent = Intent(holder.itemView?.context, DetailActivity::class.java)
                intent.putExtra("name",model.getProduct(position).name )
                intent.putExtra("price",model.getProduct(position).price )
                intent.putExtra("id",model.getProduct(position).id)
                ContextCompat.startActivity(holder.itemView.context,intent,null)
            }
        }
    }
}